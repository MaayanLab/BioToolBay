/*
//The widgets for the interactive scatter plot.
*/

var Legend = Backbone.View.extend({
	// A view for the legends of the Scatter3dView
	// tagName: 'svg',
	defaults: {
		container: document.body,
		scatterPlot: Scatter3dView,
		w: 300,
		h: 800,
	},

	initialize: function(options){
		if (options === undefined) {options = {}}
		_.defaults(options, this.defaults)
		_.defaults(this, options)
		this.setUpDOMs();
		// render if the scatterPlot changed
		this.listenTo(this.scatterPlot, 'shapeChanged', this.render)
		this.listenTo(this.scatterPlot, 'colorChanged', this.render)
     	this.listenTo(this.scatterPlot,'networkChanged',this.render)  
     	this.listenTo(this.scatterPlot,'testChanged',this.render) 
	},

	setUpDOMs: function(){
		// set up DOMs for the legends
		this.el = d3.select(this.container)
			.append('svg')
			.attr('id', 'legend')
			.attr('width', this.w)
			.attr('height', this.h);

		this.g = this.el.append('g')
			.attr('class', 'legend')
			.attr('transform', 'translate(10, 20)');
		// this.g.append('g')
		// 	.attr('id', 'legendShape')
		// 	.attr("class", "legendPanel")
		// 	.attr("transform", "translate(0, 0)");
		this.g.append('g')
			.attr('id', 'legendColor')
			.attr("class", "legendPanel")
			//.attr("transform","translate(100,0)"");
			.attr("transform", "translate(0, 0)");
		// this.g.append('g')
		// 	.attr('id','topn')
		// 	.attr("class","topn")
		// 	.attr("transform","translate(100,0)");
	},

	render: function(){
		// set up legend
		// shape legend
		var scatterPlot = this.scatterPlot;
		// var legendShape = d3.legend.symbol()
		// 	.scale(scatterPlot.shapeScale)
		// 	.orient("vertical")
		// 	.title(scatterPlot.shapeKey);
		// this.g.select("#legendShape")
		// 	.call(legendShape);

		// color legend
		//fix colorscale if coloring by score, where colorscale is an array
		var colorscale=scatterPlot.colorScale;
		if(colorscale.constructor === Array){
			var colorscale=scatterPlot.colorScaleBasic;
		}

		
		var legendColor = d3.legend.color()
			//.title(scatterPlot.colorKey)
			.title('library')
			.shapeWidth(20)
			.cells(5)
			.scale(colorscale);
			//.scale(scatterPlot.colorScale);
		//var legendScores = d3.legend.


		this.g.select("#legendColor")
			.call(legendColor);
		// this.g.select("#topn")
		// 	.call(function(d){getTopN();});

		return this;
	},

});

var Scores = Backbone.View.extend({
	defaults: {
		container: document.body,
		scatterPlot: Scatter3dView,
		w: 300,
		h: 800,
		// testtype:null,
		// graphtype:null,
		// result_id:null,
	},

	initialize: function(options){
		if (options === undefined) {options = {}}
		_.defaults(options, this.defaults)
		_.defaults(this, options)
		// render if the scatterPlot changed
		//this.render();
		this.listenTo(this.scatterPlot, 'shapeChanged', this.render)
		this.listenTo(this.scatterPlot, 'colorChanged', this.render)
     	this.listenTo(this.scatterPlot,'networkChanged',this.render)  
     	this.listenTo(this.scatterPlot,'testChanged',this.render) 



	},
	render: function(){

		//this.el=this.getTopN();
     	var globaldata=null;
     	//var table;		
		$("#table").remove();
		
		this.getTopN();
		console.log();
		//this.tabulate

		//return this;
	},
	getTopN: function(result_id,testtype,graphtype){
		var result_id=this.scatterPlot.model.resultid;
		var testtype=this.scatterPlot.testtype;
		var graphtype=this.scatterPlot.graphtype;
		var self=this;
		$.getJSON('topn/'+testtype+'/'+graphtype+"/"+result_id,
			function(result){
				//returns an object array that isnt evaluated
				globaldata=result;
				(self.tabulate());
		});
			

		
	},
	tabulate: function(data){
		var data=globaldata;
		columns=['geneset','library','score']
		columns2=['geneset','library','p-value']
 		var table = d3.select(this.container).append('table').attr("id","table");
 		var thead = table.append('thead');
 		var tbody=table.append('tbody');
 		thead.append('tr')
 			.selectAll('th')
 			.data(columns2).enter()
 			.append('th')
 			.text(function (column){return column;});
 		var rows = tbody.selectAll('tr')
 			.data(data)
 			.enter()
 			.append('tr');
 		var cells = rows.selectAll('td')
 			.data(function (row){
 				return columns.map(function (column){
 					return {column: column, value: row[column]};
 				});
 			})
 			.enter()
 			.append('td')
 				.text(function (d){return d.value;});
 		return table;
 	},




});


var Controler = Backbone.View.extend({

	defaults: {
		container: document.body,
		scatterPlot: Scatter3dView,
		w: 300,
		h: 800,
	},

	initialize: function(options){
		if (options === undefined) {options = {}}
		_.defaults(options, this.defaults)
		_.defaults(this, options)

		this.model = this.scatterPlot.model;

		this.listenToOnce(this.model, 'sync',this.render)

		var scatterPlot = this.scatterPlot;

		var result_id=this.model.resultid;

		this.listenTo(scatterPlot, 'shapeChanged', this.changeSelection);

		scatterPlot.listenTo(this, 'shapeChanged', function(selectedMetaKey){
			scatterPlot.shapeBy(selectedMetaKey);
		});
		scatterPlot.listenTo(this, 'colorChanged', function(selectedMetaKey){
			scatterPlot.colorBy(selectedMetaKey);
		});
    
       scatterPlot.listenTo(this,'networkChanged',function(selectedMetaKey){
          scatterPlot.changeNetworkBy(selectedMetaKey)
       });     

       this.listenTo(scatterPlot,'networkChanged',this.changeSelection);

       scatterPlot.listenTo(this,'testChanged', function(selectedMetaKey){
       		scatterPlot.changeTestBy(selectedMetaKey);
       });

       this.listenTo(scatterPlot,'testChanged',this.changeSelection);
		    
    

	},

	render: function(){
		// set up DOMs for the controler
		this.el = d3.select(this.container)
			.append('div')
			 .attr('id', 'controls')
			.style('width', this.w)
			.style('height', this.h);

		var model = this.model;
		// filter out metas used as index
		var metas = _.filter(model.metas, function(meta){ return meta.nUnique < model.n; });
		var self = this;


		// Shapes: 
		// var shapeControl = this.el.append('div')
		// 	.attr('class', 'form-group');
		// shapeControl.append('label')
		// 	.attr('class', 'control-label')
		// 	.text('Shape by:');

		// var shapeSelect = shapeControl.append('select')
		// 	.attr('id', 'shape')
		// 	.attr('class', 'form-control')
		// 	.on('change', function(){
		// 		var selectedMetaKey = d3.select('#shape').property('value');
		// 		self.trigger('shapeChanged', selectedMetaKey)
		// 	});

		// var shapeOptions = shapeSelect
		// 	.selectAll('option')
		// 	.data(['library']).enter()
		// 	//.data(_.pluck(metas, 'name')).enter()
		// 	.append('option')
		// 	.text(function(d){return d;})
		// 	.attr('value', function(d){return d;});

		// Colors
		// var colorControl = this.el.append('div')
		// 	.attr('class', 'form-group')
		// colorControl.append('label')
		// 	.attr('class', 'control-label')
		// 	.text('Color by:');

		// var colorSelect = colorControl.append('select')
		// 	.attr('id', 'color')
		// 	.attr('class', 'form-control')
		// 	.on('change', function(){
		// 		var selectedMetaKey = d3.select('#color').property('value');
		// 		self.trigger('colorChanged', selectedMetaKey)
		// 	});
		// var colormetas=_.pluck(metas,'name');
		// colormetas.splice(0,1);
		// colormetas.splice(1,1);

		// var colorOptions = colorSelect
		// 	.selectAll('option')
		// 	.data(colormetas).enter()
		// 	//.data(_.pluck(metas, 'name')).enter()
		// 	.append('option')
		// 	.text(function(d){return d;})
		// 	.attr('value', function(d){return d;});
        
        
       var networkControl=this.el.append('div')
           .attr('class','form-group')
          networkControl.append('label')
          .attr('class','control-label')
          .text('Choose Gene Set Category:');
       var networkSelect=networkControl.append('select')
           .attr('id','network')
           .attr('class','form-control')
           .on('change',function(){
                var selectedMetaKey=d3.select('#network').property('value');
                self.trigger('networkChanged',selectedMetaKey)
           });                
        var networkOptions=networkSelect
           .selectAll('option')
           .data(['Diseases and Drugs','Transcription','Cell Type','Ontology']).enter()
           .append('option')
           .text(function(d){return d;})
           .attr('value',function(d){return d;});

        if(this.model.resultid){
        	var testControl=this.el.append('div')
        		.attr('class','form-group')
        		testControl.append('label')
        		.attr('class','control-label')
        		.text('Choose Test Type');
        	var testSelect=testControl.append('select')
        		.attr('id','test')
        		.attr('class','form-control')
        		.on('change',function(){
        			var selectedMetaKey=d3.select('#test').property('value');
        			self.trigger('testChanged',selectedMetaKey)
        		});
        	var testOptions=testSelect
        		.selectAll('option')
        		.data(['Fisher Test','Chi Square']).enter()
        		.append('option')
        		.text(function(d){return d;})
        		//is the attr needed?
        		.attr('value',function(d){return d;});
        }
 
		return this;
	},

	changeSelection: function(){
		// change the current selected option to value
		$('#shape').val(this.scatterPlot.shapeKey); 
		$('#color').val(this.scatterPlot.colorKey);
		$('#network').val(this.scatterPlot.networkKey);
		if(this.model.resultid){
			console.log('changetesttypecalled');
			$('#test').val(this.scatterPlot.testKey);
		}
	},

});

var SearchSelectize = Backbone.View.extend({
	// selectize to search for drugs by name
	defaults: {
		container: document.body,
		scatterPlot: Scatter3dView,
	},

	initialize: function(options){
		if (options === undefined) {options = {}}
		_.defaults(options, this.defaults)
		_.defaults(this, options)

		this.model = this.scatterPlot.model;

		this.listenTo(this.model, 'sync', this.render);

		var scatterPlot = this.scatterPlot;
		// scatterPlot highlightQuery once selectize is searched
		scatterPlot.listenTo(this, 'searched', function(query){
			scatterPlot.highlightQuery(query, 'perturbation');
		});

	},

	render: function(){
		// get autocomplete list
		var autocompleteList = _.unique(this.model.getAttr('perturbation'));
		var options = [];
		for (var i = 0; i < autocompleteList.length; i++) {
			var name = autocompleteList[i];
			options.push({value: name, title: name});
		};

		// set up the DOMs
		// wrapper for SearchSelectize
		var searchControl = $('<div class="form-group" id="search-control"></div>')
		searchControl.append($('<label class="control-label">Search for drugs:</label>'))

		this.$el = $('<select id="search" class="form-control"></select>');
		searchControl.append(this.$el)
		$(this.container).append(searchControl)

		this.$el.selectize({
			valueField: 'value',
			labelField: 'title',
			searchField: 'title',
			sortField: 'text',
			options: options,
			create:false
			});

		// on change, trigger('searched', query)
		var self = this;
		this.$el[0].selectize.on('change', function(value){
			self.trigger('searched', value)
		});
	},

});


var SigSimSearchForm = Backbone.View.extend({
	//The <form> version of signature similarity search
	defaults: {
		container: "#controls1",
		scatterPlot: Scatter3dView,
		example: {
			up: ["HSD3B2","BEX1","STAR","TXNDC5","MRO","LDHB","LDHA","RPS29","NPTN","PTS","NDUFA12","MT2A","LTA4H","RPSA","H2AFZ","HSD11B1","COX2","HNRNPA1P10","IARS","SLC47A1","TMEM14B","SH3KBP1","PIGP","HIGD1A","PARK7","BOLA3","CYP11A1","SLC25A3","MMADHC","RPL9","TMEM45A","MRFAP1","COX7A2","LOC100507328","FDX1","LUM","RPL4","DPM1","TMEM123","CRELD2","SLC46A3","ALDH9A1","SLC26A2","GPX1","LGALS1","RPL22L1","SPCS1","RPL6","GMNN","TMSB10","GAPDH","UQCRQ","KPNA2","DYNLT1","FAM96A","PPIB","RAB13","SPPL2A","DYNLL1","OAZ1","USMG5","CHN1","HMGN3","SMCO4","RPLP0P6","HIST1H2BK","HTRA1","PPA1","HAT1","RPS26","PLOD2","PRDX1","LOC100507039","RPL39","SELK","LHCGR","EEF1B2","SOD1","PRKAR2B","RBX1","HSPA8","DHCR24","ANXA2P2","BNIP3","RPS13","COMMD3","ARF4","IMPA1","RPS4X","BASP1","UQCRFS1","MGARP","RPS14P3","KTN1","RPLP0","RPS11","AMIGO2","SEC31B","PDIA6","ATP5B","C20orf24","TMEM14C","SCP2","MRPL3","GOT2","PSMD2","MANF","HNRNPK","ACE2","PSMA1","LGALS12","RBM14","MRPS24","PSMD14","ATP5J","PRDX4","MT1E","RPS5","C14orf166","SLIRP","ACADM","LAP3","ODC1","NGFRAP1","ANXA5","TPST1","ATP5L","LOC100509635","CXCL6","ETFA","SACM1L","TOB1","GBE1","COMMD8","TMEM167A","ZMPSTE24","POMP","TUBB2A","CELA2A","SNRPG","COX6C","PCNA","MT1HL1","HSPA5","NDUFAB1","PGAM1","MFSD1","MYL12B","NDUFS6","SRP9","RPS21","MLLT11","EIF4A3","MICU2","LYPLA1","ROBO1","CHCHD2","HMGN1","OSTC","RYR3","NUDT9","ITGAV","RPL26L1","TMEM263","SRP14","NNMT","AIM1","C3","VCAM1","TUBA4A","GBP2","ALDH3A2","RPL34","NRIP3","MINPP1","MXRA5","NDUFA4","CDK2AP1","RPL22","RPL27","GNG10","CETN2","ATP2C1","RAB1A","RAP1B","TMEM14A","DECR1","UCHL3","TSPYL4","LINC00622","WBP5","TMA7","RRAGA","ERMP1","PSME2","ENOPH1","TGFBR3","GTF3C6","BZW1","LOC100508591","SEC61G","LRP11","PSMB4","DPY19L3","CUTA","TOMM5","COL5A2","MT1X","RPL41","NDUFB5","TAX1BP1","TMEM50A","GFPT2","AGL","RPL36A","RPL36AL","HSP90AA1","MT1F","HSD17B10","SEC13","C10orf32","TMEM133","LOC728825","RPS17","MEIS2","UBC","LINC00998","CYB561A3","UNC50","HIST1H2AC","APOO","PEG3","PSMB3","AADAC","RBBP7","PTTG1","RPS8","PORCN","SURF4","HSPE1","BET1","RPS7","HLA-DRB5","MIR22HG","ATP5G1","TDP2","KDELR2","TMED7","PSMC6","SRP19","GPR158","C1QBP","RPS18","DDX1","ANXA2","H3F3AP4","HIST1H1C","DNAJA1","LAPTM4A","PSMB5","PGRMC1","MRPL33","NME1","NPTX2","NDUFA8","TXNDC15","UBB","DNAJB11","PLGRKT","IFITM3","COX1","NIPSNAP3A","RPL24","PSMC1","SLC12A8","DAD1","IGDCC4","RPL32","C6orf211","TCEB1","NDUFAF1","NAA20","DLD","VBP1","CHCHD1","DBI","RPL23A","RPL21","VIMP","GBP3","PSMC2","C18orf32","NDUFA6","MSMO1","TIMM21","BMI1","GLIPR1","EZH2","C14orf119","UQCRH","SLC25A5","DHRS9","MT1H","OST4","HAPLN1","NID2","RPN2","TMEM181","PDHB","ATRAID","PSMD12","SKP1","ITGAE","NIT2","TCEAL8","NOP10","ATP5I","PSMA2","PSMA7","KIAA1462","CETN3","GALNT1","LOC100506748","RAN","ILF2","SUCLA2","P4HB","MAGEH1","GPX8","LINC00493","TNFAIP3","RAPGEF4","METTL23","DDX21","MRPL53","GLRX","TCEAL7","TST","IPO7","GCSHP5","HLA-DRB1","TRIAP1","SLC35B1","C4orf3","ABAT","ARCN1","RPL30","TUBB6","YBX1","RNF4","ENC1","PGRMC2","TAF9","TBC1D23","C1QTNF1-AS1","RRM2","JKAMP","CD59","RPL26","RPL10","PDIA3","HMGN2","OAT","DIRAS3","RPL7A","SLTM","GSKIP","TCEAL4","SLC2A10","TM2D3","CXCL1","TIMP1","SERINC5","MTCH2","HMGCR","GXYLT2","ADI1","FHL2","RPL3","MRPS33","NARS","FAM174A","NDUFC2","PITPNB","TEKT4P2","TMEM126A","TPRKB","TMEM69","PTX3","RCN2","HNRNPA3","MGST2","NRIP1","RPS27L","ETF1","GNG5","BIRC2","HADHB","SNX6","HSBP1","CLIC1","H3F3B","EIF2S1","C15orf48","PRDX6","TCEAL1","ATP6V0B","MLEC","GRPEL1","DPYSL2","CXCL8","SPCS3","SEC23B","NMI","TMEM208","EBNA1BP2","GSTA3","NAT1","IGSF11","FRG1","POLR2K","RNF11","IL7R","NCOA4","SEC11C","DUOXA2","FAM177A1","TSPAN12","PDIA4"
],
		}, 
		action: 'search',
		result_id: undefined
	},

	initialize: function(options){
		if (options === undefined) {options = {}}
		_.defaults(options, this.defaults)
		_.defaults(this, options)

		this.model = this.scatterPlot.model;

		this.listenTo(this.model, 'sync', this.render);

 

	},

	render: function(){
		$("#geneSet").remove();
		$("#download").remove();
		//set up DOMs
		var form = $('<form method="post" id="geneSet"></form>');
		form.attr('action', this.action);

		form.append($('<h4>Signature Similarity Search:</h4>'))
		var upGeneDiv = $('<div class="form-group">')
		upGeneDiv.append($('<label for="upGenes" class="control-label">Up genes</label>'));
		this.upGeneTa = $('<textarea name="upGenes" rows="5" class="form-control" required></textarea>');
		upGeneDiv.append(this.upGeneTa);


		var self = this;
		var exampleBtn = $('<button class="btn btn-xs pull-left">Example</button>').click(function(e){
			e.preventDefault();
			self.populateGenes(self.example.up);
		});

		var clearBtn = $('<button class="btn btn-xs">Clear</button>').click(function(e){
			e.preventDefault();
			self.populateGenes([], []);
		});

		var submitBtn = $('<input type="submit" class="btn btn-xs pull-right" value="Search"></input>');

		var downloadBtn = $('<input type="submit" class="btn btn-xs" value="Download"></input>');

		var downloadform = $('<form method="post" id="download"></form>');
		downloadform.attr('action','result/download/'+this.result_id);

		//append everything to form
		form.append(upGeneDiv)
		form.append(exampleBtn)
		form.append(clearBtn)
		form.append(submitBtn)
		downloadform.append(downloadBtn)
		//append form the container
		$(this.container).append(form)
		//populate input genes if result_id is defined
		if (this.result_id){
		//	this.model.Controler.render();
			this.populateInputGenes();
			$(this.container).append(downloadform)
		}
	
	},

	populateGenes: function(upGenes){  // , dnGenes){
		//To populate <textarea> with up/down genes
		this.upGeneTa.val(upGenes.join('\n'));
	},

	populateInputGenes: function(result_id){
		// Populate <textarea> with input up/down genes retrieved from the DB
		var self = this;
		$.getJSON('inputgenes/'+this.result_id, function(geneSet){
			self.populateGenes(geneSet); 
		});
	},
});

//var ResultModalBtn = Backbone.View.extend({
	// The button to toggle the modal of similarity search result
//	defaults: {
//		container: document.body,
//		scatterPlot: Scatter3dView,
//		result_id: undefined
//	},
	
//	initialize: function(options){
//		if (options === undefined) {options = {}}
//		_.defaults(options, this.defaults)
//		_.defaults(this, options)

//		this.model = this.scatterPlot.model;

//		this.listenTo(this.model, 'sync', this.render);

//	},

//	render: function(){
		// set up the button
//		this.button = $('<a id="modal-btn" class="btn btn-info">Show detailed results</a>');
//		var modal_url = 'result/modal/' + this.result_id;

//		this.button.click(function(e){
//			e.preventDefault();
//			$('#result-modal').modal('show')
//			$(".modal-body").load(modal_url);
//		});
//		$(this.container).append(this.button);
//	},

//});

// var ResultModal = Backbone.View.extend({
// 	// Used for toggling the mouseEvents of the scatterPlot.
// 	defaults: {
// 		scatterPlot: Scatter3dView,
// 	},

// 	initialize: function(options){
// 		if (options === undefined) {options = {}}
// 		_.defaults(options, this.defaults)
// 		_.defaults(this, options)

// 		this.model = this.scatterPlot.model;
// 		this.listenTo(this.model, 'sync', this.toggleScatterPlotMouseEvents);

// 	},

// 	toggleScatterPlotMouseEvents: function(){
// 		this.$el = $('#result-modal');
// 		var scatterPlot = this.scatterPlot;
// 		this.$el.on('show.bs.modal', function(e){
// 			scatterPlot.removeMouseEvents()
// 		});
// 		this.$el.on('hide.bs.modal', function(e){
// 			scatterPlot.addMouseEvents()
// 		});
// 	},

// });

var Overlay = Backbone.View.extend({
	// An overlay to display current status.
	tagName: 'div',
	defaults: {
		container: document.body,
		scatterPlot: Scatter3dView,
	},

	initialize: function(options){
		if (options === undefined) {options = {}}
		_.defaults(options, this.defaults)
		_.defaults(this, options)
		
		this.render();
		this.changeMessage('Retrieving data from the server...');

		// finished retrieving data
		var self = this;
		this.listenTo(this.scatterPlot.model, 'sync', function(){
			self.changeMessage('Data retrieved. choose a geneset ...');
		});
		// finished rendering
		this.listenTo(this.scatterPlot, 'shapeChanged',
			this.remove)
	},

	render: function(){
		var w = $(this.container).width(),
			h = $(this.container).height();
		this.el = d3.select(this.container)
			.append(this.tagName)
			.style('width', w)
			.style('height', h)
			.style('z-index', 10)
			.style('position', 'absolute')
			.style('right', '0px')
			.style('top', '0px')
			.style('background-color', 'rgba(50, 50, 50, 0.5)')
			.style('cursor', 'wait');

		this.msgDiv = this.el.append('div')
			.style('z-index', 11)
			.style('position', 'absolute')
			.style('text-align', 'center')
			.style('width', '100%')
			.style('top', '50%')
			.style('font-size', '250%');
		
		return this;
	},

	changeMessage: function(msg){
		this.msgDiv.text(msg);
	},

	remove: function(){
		this.changeMessage('Rendering completed')
		// COMPLETELY UNBIND THE VIEW
		this.undelegateEvents();
		// Remove view from DOM
		this.el.remove()
		// this.remove();  
		// Backbone.View.prototype.remove.call(this);
	},
});

