var textures = new Textures()
//make an array of objects that somehow relate the python array/list to here


var sd = new ScatterData({

	url: 'graph/1'
})

var sdv = new Scatter3dView({
	model: sd,
	textures: textures,
	// pointSize: 0.1, 
	pointSize: 12,
	is3d: false,
	colorKey: 'cell',
	shapeKey: 'time',
	labelKey: ['sig_id'],
})

var legend = new Legend({scatterPlot: sdv, h: window.innerHeight})

var controler = new Controler({scatterPlot: sdv, h: window.innerHeight, w: 200})

//var search = new SearchSelectize({scatterPlot: sdv, container: "#controls"})

//var sigSimSearch = new SigSimSearchForm({scatterPlot: sdv, container: "#controls"})

var overlay = new Overlay({scatterPlot: sdv})
