var express = require('express');
var app = express();
var bodyParser = require('body-parser');
var fileUpload = require('express-fileupload');
const uuid = require('uuid/v4');
var path = require('path');

app.use(express.static(path.join(__dirname, 'videos')));

app.use(bodyParser.json());
app.use(fileUpload());

app.get('/:id',function (req, res)  {
	videoLink = req.params.id;
	type = path.extname(videoLink);
	console.log(videoLink)
	console.log(type)
	res.set('Content-Type', 'text/html');
	res.send(new Buffer('<video src="videos/"'+videoLink +'type="video/'+ type+'" controls>Your browser does not support the video tag.</video>'));
});

app.post('/upload', function (req,res)  {
	//console.log(req.files.video);
	//console.log(req);
	//console.log('Over');
	
	let sampleFile = req.files.video;
	type = path.extname(req.body.path);
	fileName = uuid().toString() + type
	sampleFile.mv('videos/'+fileName, (err) => {
		if(err)
			return res.status(500).send(err);
		res.json({link: fileName});
	});
	
});

app.listen(3000, function () {
  console.log('Example app listening on port 3000!');
});