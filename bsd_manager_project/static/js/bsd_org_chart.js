odoo.define('bsd_manager_project.org_chart_view', function(require){
    "use strict";
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var ajax = require('web.ajax')
    var Context = require('web.Context');
    var Qweb = core.qweb;
    var _t = core._t;
    var _lt = core._lt;

    var org_chart_view = AbstractAction.extend({
        template: 'bsd_manager_project.org_chart',
        init: function(parent,context){
            this._super(parent, context);
            var self = this
            var data = [];
            self._rpc({
                model: 'bsd.project',
                method: 'search_read',
                fields:['id','name']
            }).then(function(data){
                self.data = data
                self.render()
            })
            self.render()
        },
        render: function(){
            var self = this;
            self.select_project()
//            self.drawChart()
        },
        select_project: function(){
            var self = this
            var s = $('#select')
            console.log('select')
            console.log(s)
            _.each(self.data, function (item,index,data){
                console.log(item.name)
                var optionValue = item.id;
                var optionText = item.name;
                s.append(`<option value="${optionValue}">${optionText}</option>`)
            })
            self.drawChart(parseInt(s.val()),$("#select option:selected").text())
            s.change(function(){
                self.drawChart(parseInt(s.val()),$("#select option:selected").text())
            })
        },
        drawChart: function (id_project,name_project) {
            var self = this
            console.log("render")
            console.log(id_project)
            console.log(name_project)
            console.log(self.data)
            self._rpc({
                model: 'bsd.screen',
                method: 'search_read',
                fields: ['id','name','bsd_project_id'],
                domain: [['bsd_project_id', '=', id_project]]
            }).then(function(data_screen){
                var ids_screen = []
                _.each(data_screen, function(item,index,data_screen){
                    item.type = 'Screen'
                })
                console.log("ids_screen:" + ids_screen.toString())
                console.log(data_screen)
                self._rpc({
                    model: 'bsd.ba.request',
                    method: 'search_read',
                    fields: ['id','name', 'bsd_parent_id','bsd_screen_id'],
                    domain: [['bsd_project_id', '=',id_project],['state', '=', 'approve']]
                }).then(function (data_request){
                    var ids_request = []
                    _.each(data_request, function(item,index,data_request){
                        ids_request.push(item.id)
                    })
                    console.log("ids_request:" + ids_request.toString())
                    console.log(data_request)
                    google.charts.load('current', {packages:["orgchart"]});
                    google.charts.setOnLoadCallback(drawChart_inner);
                    function drawChart_inner(){
                        var data = new google.visualization.DataTable();
                        data.addColumn('string', 'Name');
                        data.addColumn('string', 'Manager');
                        data.addColumn('string', 'ToolTip');
                        data.addColumn('string', 'ID');
                        var temp = [[{'v':name_project, 'f':name_project +'<div style="color:red; font-style:italic">Project</div>}'},'','Project',id_project.toString()]]
                        _.each(data_screen, function(item,index,data_screen){
                            temp.push([{'v':item.name,'f':item.name +'<div style="color:red; font-style:italic">Screen</div>'},name_project,'',item.id.toString()])
                        })
                        _.each(data_request, function(item,index,data_request){
                            if (item.bsd_parent_id === false){
                                temp.push([{'v':item.name,'f':item.name +'<div style="color:red; font-style:italic">Request</div>'},name_project,'',item.id.toString()])
                            }
                            else {
                                temp.push([{'v':item.name,'f':item.name +'<div style="color:red; font-style:italic">Request</div>'},item.bsd_parent_id[1],'',item.id.toString()])
                            }
                        })
                        console.log("temp")
                        console.log(temp)
                        data.addRows(temp);
                        var d = $('div #chart')
                        console.log(d)
                        // Create the chart.
                        console.log(data);
                        _.each(data['wg'], function(item,index,data_wg){
                        data.setRowProperty(index, 'style', 'border: 0px ');
                        });
                        var chart = new google.visualization.OrgChart(d[0]);
                    // google.visualization.events.addListener(chart, 'select', selectHandler);
                    // Draw the chart, setting the allowHtml option to true for the tooltips.
                        chart.draw(data, {'allowHtml':true,'size':'medium'});
                    }
                })
            })

        },
        reload: function () {
            window.location.href = this.href;
    },
    });
    core.action_registry.add('org_chart_view', org_chart_view)
    return org_chart_view
});

