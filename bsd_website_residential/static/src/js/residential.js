odoo.define('bsd_residential_website.residential', function(require){
'use strict';
    var publicWidget = require('web.public.widget');

    publicWidget.registry.residentialRegistry = publicWidget.Widget.extend({
        selector: '.o_residential_registry',
        events: {
            'change select[id="selectMethod"]': '_onMethodChange',
            'change select[id="selectUnit"]': '_onUnitChange',
            'change select[class="onchangeRes"]': '_onResChange',
            'click button[id="post-btn"]': '_clickPostForm',
            'click button[id="add-create-line"]': '_clickAddLine',
            'click button[id="add-res-line"]': '_clickAddLineRes',
            'click button[id="remove-create-line"]': '_clickRemoveLine',
        },

        init: function(){
            console.log("odoo")
            console.log($('#selectMethod')[0].value)
            console.log($('#sub-res'))
            if ($('#selectMethod')[0].value == 'create'){
                console.log("chạy vào đây")
                $('#add-res').show()
                $('#sub-res').hide()
            }
        },

        start: function(){
            var def = this._super.apply(this, arguments);
            console.log("Đã chạy vào đây")
//            console.log(arguments)
            return def;
        },

        _onMethodChange: function(){
            console.log("onchange method")
            console.log($('#selectMethod')[0].value)
            if ($('#selectMethod')[0].value == 'create' || $('#selectMethod')[0].value == 'host' ){
                $('#add-res').show()
                $('#sub-res #residential-line').children().remove()
                $('#sub-res').hide()
            }
            else{
                $('#add-res').hide()
                $('#add-res #registry-line').children().remove()
                $('#sub-res').show()
            }
        },

        _onUnitChange: function(){
            console.log("onchange unit")
            if ($('#selectMethod')[0].value == 'create' || $('#selectMethod')[0].value == 'host'){
                $('#add-res #registry-line').children().remove()
            }
            else{

                $('#sub-res #residential-line').children().remove()
            }

        },

        _onResChange: function(event){
            console.log("change res")
            var option = $('option:selected', $(event.target)).attr('relationship');
            console.log(option)
            console.log($(event.target).parent().parent().children('td:last').children('select').val(option))
        },

        _clickPostForm: function(){
            console.log("click button");

            const serialize_form = form =>
                Array.from(new FormData(form).entries())
                     .reduce((m, [ key, value ]) => Object.assign(m, { [key]: value }), {})
            ;

            console.log($('#reg-form')[0])
            var data_post = serialize_form($('#reg-form')[0])

            if ($('#selectMethod')[0].value == 'create' || $('#selectMethod')[0].value == 'host'){
                var trs = $('#registry-line tr')
                console.log(trs)
                var registry_line_s = []
                _.each(trs, function(item,index,trs){
                    console.log("in ra item")
                    var registry_line = [0,0,{
                        name: item.cells[0].firstElementChild.value,
                        birthday: item.cells[1].firstElementChild.value,
                        cmnd: item.cells[2].firstElementChild.value,
                        vat: item.cells[3].firstElementChild.value,
                        function: item.cells[4].firstElementChild.value,
                        email: item.cells[5].firstElementChild.value,
                        mobile: item.cells[6].firstElementChild.value,
                        relationship_id: parseInt(item.cells[7].firstElementChild.value)
                        }
                    ]
                    registry_line_s.push(registry_line)
                })
                data_post.bsd_line_ids = registry_line_s
            }
            else{
                var trs_res = $('#residential-line tr')
                console.log('residential')
                console.log(trs_res)
                var residential_line_s = []
                _.each(trs_res, function(item,index,trs){
                    var residential_line = [0,0,{
                        bsd_residential_id: parseInt(item.cells[0].firstElementChild.value),
                        bsd_relationship_id: parseInt(item.cells[1].firstElementChild.value)
                    }]
                    residential_line_s.push(residential_line)
                })
                data_post.bsd_residential_ids = residential_line_s
            }
            console.log(data_post)
            $.ajax({
                type: 'POST',
                url: '/registry/post',
                dataType: 'json',
                data: JSON.stringify({params:data_post}),
                contentType : 'application/json',
                success: function(data) {
                console.log(data.result)
                window.location.replace("/registry/success");
        }
    });

        },

        _clickAddLine: function(){
            console.log("click add line")
            $('#registry-line').append(`
                                            <tr>
                                                <td><input type="text"></td>
                                                <td><input type="date" min="1920-01-01" max="2020-12-31"/></td>
                                                <td><input type="text"/></td>
                                                <td><input type="text"></td>
                                                <td><input type="text"/></td>
                                                <td><input type="text"/></td>
                                                <td><input type="text"/></td>
                                                <td>
                                                    <select>
                                                        <option>..</option>
                                                    </select>
                                                </td>
                                            </tr>`
                                        )
            $.ajax({
                type: 'POST',
                url: '/registry/relationship',
                dataType: 'json',
                data: JSON.stringify({params:[]}),
                contentType: 'application/json',
                success: function(data){
                    console.log(data.result)
                    _.each(data.result, function(item,index,data){
                        $('#registry-line tr:last td:last select').append(
                        `
                            <option value="${item[0]}">${item[1]}</option>
                        `)
                    })
                },
            })
        },

        _clickRemoveLine: function(){
            var tr = $('#registry-line tr:last')
            tr.remove()
        },

        _clickAddLineRes: function(){
            console.log('click add res line')
            $('#residential-line').append(`
                                            <tr>
                                                <td>
                                                    <select class="onchangeRes">
                                                        <option>..</option>
                                                    </select>
                                                </td>
                                                <td>
                                                    <select>
                                                        <option>..</option>
                                                    </select>
                                                </td>
                                            </tr>`
                                        )
            $.ajax({
                type: 'POST',
                url: '/registry/relationship',
                dataType: 'json',
                data: JSON.stringify({params:[]}),
                contentType: 'application/json',
                success: function(data){
                    console.log(data.result)
                    _.each(data.result, function(item,index,data){
                        $('#residential-line tr:last td:last select').append(
                        `
                            <option value="${item[0]}">${item[1]}</option>
                        `)
                    })
                    $.ajax({
                        type: 'POST',
                        url: '/registry/residential',
                        dataType: 'json',
                        data: JSON.stringify({params:{bsd_unit_id : parseInt($('#selectUnit')[0].value)}}),
                        contentType: 'application/json',
                        success: function(data){
                            console.log(data)
                            _.each(data.result, function(item, index, data){
                                console.log(item)
                                $('#residential-line tr:last td:first select').append(
                                    `
                                    <option value="${item.id}" relationship="${item.bsd_relationship_id}">${item.name}</option>
                                    `
                                )
                            })
                        }
                    })
                },
            })

        },
    })

    publicWidget.registry.residentialService = publicWidget.Widget.extend({
        selector: '.o_residential_service',
        events:{
            'change select[id="selectService"]' : '_onServiceChange',
            'change select[id="selectUnit"]' : '_onUnitChange',
            'click button[id="add-vehicle-line"]' : '_clickAddVehicleLine',
            'click button[id="remove-vehicle-line"]' : '_clickRemoveVehicleLine',
            'click button[id="post-btn"]': '_clickPostForm',
        },
        init: function(){
            console.log("chạy phần service")
            var self = this;
            $.ajax({
                type: 'POST',
                url: '/service/parking',
                dataType: 'json',
                data: JSON.stringify({params:[]}),
                contentType: 'application/json',
                success: function(data){
                    console.log(data)
                    self.parking = data.result.parking_service
                    console.log(self.parking)
                    self._onServiceChange()
                }
            });
        },

        start: function(){
            var def = this._super.apply(this, arguments);
            console.log("Đã chạy vào đây")
            return def;
        },

        _onServiceChange: function(){
            console.log('onchange service')
            var service = $('#selectService')
            var self = this
            self.group_attribute = []
            if (service.children("option:selected").attr('is-master')){
                $('#div-unit').show()
            }
            else {
                $('#div-unit').hide()
            }
            if (parseInt(service.val()) != this.parking) {

                $('#parking-service').hide()
                $('#parking-service #vehicle-line').children().remove()
                $.ajax({
                type: "POST",
                url: "/service/type",
                dataType: 'json',
                data: JSON.stringify({params:{bsd_type_id:parseInt(service[0].value)}}),
                contentType: 'application/json',
                success: function(data){
                    console.log(data)
                    $('#attribute').children().remove()
                    var data_attribute_group = _.groupBy(data.result, 'attribute_id')
                    _.each(data_attribute_group, function(item,index,data){
                        console.log(item)
                        var name_attribute =item[0].attribute_id[0][1]
                        self.group_attribute.push(item[0].attribute_id[0][0])
                        console.log(name_attribute)
                         $('#attribute').append(`
                            <div class="row">
                                <label class="col-form-label">${name_attribute}:</label>
                            </div>
                         `)
                        _.each(item, function(item,index,data){
                            if (index == 0){
                                $('#attribute div:last').append(`
                                <label class="col-form-label">
                                <input type="radio" name="${item.attribute_id[0][0]}" value="${item.id}" checked>${item.name}</input>
                                </label>
                                `)
                            }
                            else{
                               $('#attribute div:last').append(`
                                <label class="col-form-label">
                                <input type="radio" name="${item.attribute_id[0][0]}" value="${item.id}">${item.name}</input>
                                </label>
                                `)
                            }
                        })

                    })
                }
            })
            }
            else{
                $('#attribute').children().remove()
                $('#parking-service').show()
            }
        },

        _onUnitChange: function(){
            console.log("onchange unit")
            var service = $('#selectService')
            if (parseInt(service.val()) == this.parking){
                $('#vehicle-line').children().remove()
            }
        },

        _clickAddVehicleLine: function(){
            console.log("click add line")
             var service = $('#selectService')
            $('#vehicle-line').append(`
                                            <tr>
                                                <td>
                                                    <select>
                                                        <option>..</option>
                                                    </select>
                                                </td>
                                                <td><input type="text"/></td>
                                                <td><input type="text"/></td>
                                                <td><input type="text"></td>
                                                <td>
                                                    <select>
                                                        <option>..</option>
                                                    </select>
                                                </td>
                                            </tr>`
                                        )
            $.ajax({
                    type: "POST",
                    url: "/service/type",
                    dataType: 'json',
                    data: JSON.stringify({params:{bsd_type_id:parseInt(service[0].value)}}),
                    contentType: 'application/json',
                    success: function(data){
                        _.each(data.result, function(item, index, data){
                            $('#vehicle-line tr:last td:first select').append(`
                                <option value="${item.id}">${item.name}</option>
                            `)
                        })

                    }
            })
            $.ajax({
                type: 'POST',
                url: '/registry/residential',
                dataType: 'json',
                data: JSON.stringify({params:{bsd_unit_id : parseInt($('#selectUnit')[0].value)}}),
                contentType: 'application/json',
                success: function(data){
                    console.log(data)
                    _.each(data.result, function(item, index, data){
                        console.log(item)
                        $('#vehicle-line tr:last td:last select').append(
                        `
                        <option value="${item.id}">${item.name}</option>
                        `
                        )
                    })
                }
            })
        },

        _clickRemoveVehicleLine: function(){
            var tr = $('#vehicle-line tr:last')
            tr.remove()
        },

        _clickPostForm: function(){
            console.log("click button");
            var service = $('#selectService')
            var self = this
            var data_post = {}
            if (parseInt(service.val()) == this.parking){
               data_post.bsd_unit_id = parseInt($('#selectUnit').val())
               data_post.bsd_type_id = parseInt($('#selectService').val())
                var trs = $('#vehicle-line tr')
                console.log(trs)
                var vehicle_line_s = []
                _.each(trs, function(item,index,trs){
                    console.log("in ra item")
                    var vehicle_line = [0,0,{
                        bsd_type: parseInt(item.cells[0].firstElementChild.value),
                        bsd_brand: item.cells[1].firstElementChild.value,
                        bsd_license: item.cells[2].firstElementChild.value,
                        bsd_note: item.cells[3].firstElementChild.value,
                        bsd_residential_id: parseInt(item.cells[4].firstElementChild.value),
                        bsd_product_tmpl_id: parseInt(service.children("option:selected").attr('product-tmpl'))
                        }
                    ]
                    vehicle_line_s.push(vehicle_line)
                })
                data_post.bsd_vehicle_ids = vehicle_line_s
            }
            else{
                console.log('group_attribute')
                console.log(self.group_attribute)
                var attribute_ids = []
                _.each(self.group_attribute, function(item,index,data){
                    var radioValue = $("input[name='" + item.toString() + "']:checked").val()
                    attribute_ids.push(parseInt(radioValue))
                })
            }
            data_post.bsd_type_id = parseInt($('#selectService').val())
            data_post.bsd_attribute_ids = [[6,0,attribute_ids]]
            console.log(data_post)
            $.ajax({
                type: 'POST',
                url: '/service/post',
                dataType: 'json',
                data: JSON.stringify({params:data_post}),
                contentType : 'application/json',
                success: function(data) {
                console.log(data.result)
                window.location.replace("/registry/success");
                }
            });
        },
    })
})