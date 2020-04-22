from datetime import datetime
from calendar import timegm
import logging
import os
import gzip
from urllib.parse import urlparse
import re
imgTagReg = re.compile(r'(<img src=.+?>)')

from jinja2.exceptions import TemplateNotFound
import jinja2

from staticgennan import utils
from staticgennan.utils import transferFiles
from staticgennan.structure.files import get_files
from staticgennan.structure.nav import get_navigation
import staticgennan

html_head = "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><link rel='stylesheet' type='text/css' href='./css/base.css'></head><body class='%s'>"

html_footer = "</body></html>"



class DuplicateFilter:
    ''' Avoid logging duplicate messages. '''
    def __init__(self):
        self.msgs = set()

    def filter(self, record):
        rv = record.msg not in self.msgs
        self.msgs.add(record.msg)
        return rv


log = logging.getLogger(__name__)
log.addFilter(DuplicateFilter())
log.addFilter(utils.warning_filter)

def _populate_nav(page, nav, dirty=False):
    code = ""
    for i in nav:
        if i.is_section:
            code += "<a href=\"#\">{}</a>".format(i.title)+"<div class=\"section\">" +_populate_nav(page,  i.children, dirty)+ "</div>"
        elif i.is_page:
            if i.title == page.title:
                code += "<a href=\"{}\" class=\"active\">{}</a>".format(i.file.dest_path, i.title)
            else:
                code += "<a href=\"{}\">{}</a>".format(i.file.dest_path, i.title)
        elif i.is_link:
            code += "<a href=\"{}\">{}></a>".format(i.url, i.path)++"<div class=\"section\">" +_populate_nav(page, i.children, dirty)+ "</div>"
    return code

def _populate_page(page, config, files, dirty=False):
    """ Read page content from docs_dir and render Markdown. """

    try:
        # When --dirty is used, only read the page if the file has been modified since the
        # previous build of the output.
        if dirty and not page.file.is_modified():
            return

        page.read_source(config)

        page.render(config, files)

    except Exception as e:
        log.error("Error reading page '{}': {}".format(page.file.src_path, e))
        raise


def _build_page(page, config, files, nav, env, dirty=False):
    """ Pass a Page to theme template and write output to site_dir. """

    try:
        # When --dirty is used, only build the page if the file has been modified since the
        # previous build of the output.
        if dirty and not page.file.is_modified():
            return

        log.debug("Building page {}".format(page.file.src_path))

        # Activate page. Signals to theme that this is the current page.
        page.active = True

        # Render the template.
        output = html_head + page.content.strip() + html_footer

        # Write the output file.
        if output.strip():
            utils.write_file(output.encode('utf-8', errors='xmlcharrefreplace'), page.file.abs_dest_path)
        else:
            log.info("Page skipped: '{}'. Generated empty output.".format(page.file.src_path))

        # Deactivate page
        page.active = False
    except Exception as e:
        log.error("Error building page '{}': {}".format(page.file.src_path, e))
        raise

def _isPageViable(content, siteDir):
    size = len(content)
    imageTags = imgTagReg.findall(content)
    imageTags = set(imageTags)
    for i in imageTags:
        i = i.strip()
        temp = ""
        j = 10
        while i[j] != '\"' and i[j] != '\'':
            temp += i[j]
            j+=1
        dst = siteDir + '/' + temp
        dst = dst.replace('\\', '/')
        if os.path.exists(dst):
            size += os.stat(dst).st_size
    size = size / 1024 / 1024
    if size>5:
        return False
    return True

def build(config, live_server=False, dirty=False):
    """ Perform a full site build. """
    from time import time
    start = time()

    if not dirty:
        log.info("Cleaning site directory")
        utils.clean_directory(config['site_dir'])
    else:  # pragma: no cover
        # Warn user about problems that may occur with --dirty option
        log.warning("A 'dirty' build is being performed, this will likely lead to inaccurate navigation and other"
                    " links within your site. This option is designed for site development purposes only.")

    if not live_server:  # pragma: no cover
        log.info("Building documentation to directory: %s", config['site_dir'])
        if dirty and site_directory_contains_stale_files(config['site_dir']):
            log.info("The directory contains stale files. Use --clean to remove them.")

    # First gather all data from all files/pages to ensure all data is consistent across all pages.

    files = get_files(config)
    env = config['theme'].get_env()
    files.add_files_from_theme(env, config)

    nav = get_navigation(files, config)

    log.debug("Reading markdown pages.")
    for file in files.documentation_pages():
        log.debug("Reading: " + file.src_path)
        _populate_page(file.page, config, files, dirty)
    if len(files.documentation_pages()) > 1:
        for file in files.documentation_pages():
            code = _populate_nav(file.page, nav, dirty)
            if(code.strip()):
                file.page.content = "<div class=\"sidenav\">" + code.strip() + "</div>" + "<div class=\"main\">" + file.page.content + "</div>"

    # Start writing files to site_dir now that all data is gathered. Note that order matters. Files
    # with lower precedence get written first so that files with higher precedence can overwrite them.

    log.debug("Copying static assets.")
    files.copy_static_files(dirty=dirty)

    transferFiles.transferImage(config)

    log.debug("Building markdown pages.")
    for file in files.documentation_pages():
        if _isPageViable(file.page.content, config['site_dir']):
            _build_page(file.page, config, files, nav, env, dirty)
        else:
            print("Build Error: ", file.page.title, " is overloaded, reduce the size to build")

    if config['strict'] and utils.warning_filter.count:
        raise SystemExit('\nExited with {} warnings in strict mode.'.format(utils.warning_filter.count))

    log.info('Documentation built in %.2f seconds', time() - start)


def site_directory_contains_stale_files(site_directory):
    """ Check if the site directory contains stale files from a previous build. """

    return True if os.path.exists(site_directory) and os.listdir(site_directory) else False
