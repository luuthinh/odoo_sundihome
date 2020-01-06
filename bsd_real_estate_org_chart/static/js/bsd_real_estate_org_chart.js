odoo.define('bsd_real_estate_org_chart.org_chart_view', function(require){
    "use strict";
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var ajax = require('web.ajax')
    var Context = require('web.Context');
    var Qweb = core.qweb;
    var _t = core._t;
    var _lt = core._lt;

    var org_chart_view = AbstractAction.extend({
        template: 'bsd_real_estate_org_chart.org_chart',
        init: function(parent,context){
            this._super(parent, context);
            var self = this
            var data = [];
            self._rpc({
                model: 'bsd.real.estate.project',
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
            console.log("render 123456")
            console.log(id_project)
            console.log(name_project)
            console.log(self.data)
            self._rpc({
                model: 'bsd.real.estate.block',
                method: 'search_read',
                fields: ['id','complete_name'],
                domain: [['bsd_project_id', '=',id_project]]
            }).then(function (data_block){
                var ids_block = []
                _.each(data_block, function(item,index,data_block){
                    ids_block.push(item.id)
                    item.type = 'Block'
                })
                console.log("ids_block:" + ids_block.toString())
                console.log(data_block)
                self._rpc({
                    model: 'bsd.real.estate.floor',
                    method: 'search_read',
                    fields: ['id','complete_name','bsd_block_id'],
                    domain: [['bsd_block_id', 'in', ids_block]]
                }).then(function(data_floor){
                    _.each(data_floor, function(item,index,data_floor){
                        item.type = 'Floor'
                    })
                    self._rpc({
                        model: 'account.asset',
                        method: 'search_read',
                        fields: ['id','complete_name','bsd_floor_id','bsd_block_id','bsd_project_id', 'stage_id'],
                        domain: [['bsd_project_id', '=', id_project]]
                    }).then(function(data_unit){
                        _.each(data_unit, function(item,index,data_unit){
                            item.type = 'Unit'
                        })
                        console.log("unit")
                        console.log(data_unit)
                        var data_unit_group = _.groupBy(data_unit,'bsd_floor_id')
                        console.log(data_unit_group)
                        google.charts.load('current', {packages:["orgchart"]});
                        google.charts.setOnLoadCallback(drawChart_inner);
                        function drawChart_inner(){
                            var data = new google.visualization.DataTable();
                            data.addColumn('string', 'Name');
                            data.addColumn('string', 'Manager');
                            data.addColumn('string', 'ToolTip');
                            data.addColumn('string', 'ID');
                            data.addColumn('string', 'Stage')
                            var temp = [[{'v':name_project, 'f':'<div><div>' + name_project + '</div><div style="color:red; font-style:italic">Project</div></div>'},'','Project',id_project.toString(),'']]
                            _.each(data_block, function(item,index,data_block){
                                temp.push([{'v':item.complete_name,'f':'<div><div>' + item.complete_name + '</div><div font-style:italic">Block</div></div>'},name_project,item.type,item.id.toString(),''])
                            })
                            _.each(data_floor, function(item,index,data_floor){
                                temp.push([{'v':item.complete_name,'f':'<div><div>' + item.complete_name + '</div><div font-style:italic">Floor</div></div>'},item.bsd_block_id[1],item.type,item.id.toString(),''])
                            })
                            _.each(data_unit_group, function(item,index,data_unit_group){
                                var data_temp = item
                                _.each(data_temp, function(item,index,data_temp){
                                    if (index == 0){
                                    temp.push([{'v':item.complete_name,'f':'<div><div><strong>' + item.complete_name + '</strong></div><div font-style:italic">Unit</div></div>'},item.bsd_floor_id[1],item.type,item.id.toString(),item.stage_id[0].toString()])
                                    }
                                    else{
                                    temp.push([{'v':item.complete_name,'f':'<div><div><strong>' + item.complete_name + '</strong></div><div font-style:italic">Unit</div></div>'},data_temp[index - 1].complete_name,item.type,item.id.toString(),item.stage_id[0].toString()])
                                    }
                                })
                            })
                            data.addRows(temp);
                            var d = $('div #chart')
                            console.log(d)
                                // Create the chart.
                            console.log(data);
                            _.each(data['wg'], function(item,index,data_wg){
                                console.log(item.c[2].v)
                                if (item.c[2].v == 'Unit'){
                                    switch (parseInt(item.c[4].v)){
                                        case 1:
                                            data.setRowProperty(index, 'style', 'border: 0px; background: -webkit-gradient(linear, left top, left bottom, from(#FA5858), to(#cde7ee))');
                                            break;
                                        case 2:
                                            data.setRowProperty(index, 'style', 'border: 0px; background: -webkit-gradient(linear, left top, left bottom, from(#F4FA58), to(#cde7ee))');
                                            break;
                                        case 3:
                                            data.setRowProperty(index, 'style', 'border: 0px; background: -webkit-gradient(linear, left top, left bottom, from(#82FA58), to(#cde7ee))');
                                            break;
                                        case 4:
                                            data.setRowProperty(index, 'style', 'border: 0px; background: -webkit-gradient(linear, left top, left bottom, from(#58FAF4), to(#cde7ee))');
                                            break;
                                        case 5:
                                            data.setRowProperty(index, 'style', 'border: 0px; background: -webkit-gradient(linear, left top, left bottom, from(#5858FA), to(#cde7ee))');
                                            break;
                                        default:
                                            data.setRowProperty(index, 'style', 'border: 0px; background: -webkit-gradient(linear, left top, left bottom, from(#848484), to(#cde7ee))');
                                    }
                                }
                                else{
                                    data.setRowProperty(index, 'style', 'border: 0px;');
                                }
                            });
                            var chart = new google.visualization.OrgChart(d[0]);
                            google.visualization.events.addListener(chart, 'select', selectHandler);
                                // Draw the chart, setting the allowHtml option to true for the tooltips.
                            chart.draw(data, {'allowHtml':true,'size':'small'});
                            function selectHandler(e) {
                                if (chart.getSelection().length > 0){
                                    var index = chart.getSelection()[0].row
                                    var data_process = data['wg'][index]

                                    if (data_process.c[2].v == 'Block'){
                                        return self.do_action({
                                            name: _t("Block"),
                                            type: 'ir.actions.act_window',
                                            res_model: 'bsd.real.estate.block',
                                            view_mode: 'form',
                                            views: [[false, 'form']],
                                            target: 'main',
                                            res_id: parseInt(data_process.c[3].v)
                                        })
                                    }
                                    else if (data_process.c[2].v == 'Project'){
                                        return self.do_action({
                                            name: _t("Project"),
                                            type: 'ir.actions.act_window',
                                            res_model: 'bsd.real.estate.project',
                                            view_mode: 'form',
                                            views: [[false, 'form']],
                                            target: 'main',
                                            res_id: parseInt(data_process.c[3].v)
                                        })
                                    }
                                    else if (data_process.c[2].v == 'Floor'){
                                        return self.do_action({
                                            name: _t("Floor"),
                                            type: 'ir.actions.act_window',
                                            res_model: 'bsd.real.estate.floor',
                                            view_mode: 'form',
                                            views: [[false, 'form']],
                                            target: 'main',
                                            res_id: parseInt(data_process.c[3].v)
                                        })
                                    }
                                    else if (data_process.c[2].v == 'Unit'){
                                        console.log("debug tại đây")
                                        var view_id = false
                                        self._rpc({
                                            model: 'ir.ui.view',
                                            method: 'search_read',
                                            fields: ['id','name'],
                                            domain: [['name', '=', 'bsd.account.asset.form']]
                                        }).then(function(data_unit){
                                            view_id = data_unit[0].id
                                            console.log("account asset 1")
                                            console.log(view_id)
                                            return self.do_action({
                                                name: _t("unit"),
                                                type: 'ir.actions.act_window',
                                                res_model: 'account.asset',
                                                view_mode: 'form',
                                                views: [[view_id, 'form']],
                                                target: 'main',
                                                res_id: parseInt(data_process.c[3].v)
                                            })
                                        })
                                    }
                                }
                            }
                        }
                    })
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

