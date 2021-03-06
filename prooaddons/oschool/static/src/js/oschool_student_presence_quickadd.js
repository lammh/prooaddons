openerp.oschool = function (instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.web.oschool = instance.web.oschool || {};

    instance.web.views.add('tree_oschool_transport_presence_quickadd', 'instance.web.oschool.QuickAddList');
    instance.web.oschool.QuickAddList = instance.web.ListView.extend({
        init: function() {
            this._super.apply(this, arguments);
            this.zones = [];
            this.current_zone = null;
            this.default_zone = null;

            this.periods = [];
            this.current_period = null;
            this.default_period = null;

            this.days = [];
            this.current_day = null;
            this.default_day = null;
        },
        start:function(){
            var tmp = this._super.apply(this, arguments);
            var self = this;
            var defs = [];
            this.$el.parent().prepend(QWeb.render("OschoolTransportPresenceQuickAdd", {widget: this}));

            this.$el.parent().find('.oe_oschool_select_zone').change(function() {
                    self.current_zone = this.value === '' ? null : parseInt(this.value);
                    self.do_search(self.last_domain, self.last_context, self.last_group_by);
                });

            this.$el.parent().find('.oe_oschool_select_period').change(function() {
                self.current_period = this.value === '' ? null : parseInt(this.value);
                self.do_search(self.last_domain, self.last_context, self.last_group_by);
            });

            this.$el.parent().find('.oe_oschool_print').click(function() {
                if(self.current_period == null
                    || self.current_period == ''
                    || self.current_zone == null
                    || self.current_zone == '')
                {
                    alert( "Choose the period and the zone first!" );
                }else{
                    defs.push(mod.call("print_report", [self.current_period, self.current_zone]).then(function(result) {
                        self.do_action(result);
                    }));
                }
            });

            this.$el.parent().find('.oe_oschool_select_day').change(function() {
                self.current_day = this.value === '' ? null : parseInt(this.value);
                self.do_search(self.last_domain, self.last_context, self.last_group_by);
            });


            this.on('edit:after', this, function () {
                self.$el.parent().find('.oe_oschool_select_zone').attr('disabled', 'disabled');
                self.$el.parent().find('.oe_oschool_select_period').attr('disabled', 'disabled');
                self.$el.parent().find('.oe_oschool_select_day').attr('disabled', 'disabled');
            });
            this.on('save:after cancel:after', this, function () {
                self.$el.parent().find('.oe_oschool_select_zone').removeAttr('disabled');
                self.$el.parent().find('.oe_oschool_select_period').removeAttr('disabled');
                self.$el.parent().find('.oe_oschool_select_day').removeAttr('disabled');
            });
            var mod = new instance.web.Model("oschool.student_transport_presence", self.dataset.context, self.dataset.domain);
            defs.push(mod.call("default_get", [['zone_id','period_id','dayNum'],self.dataset.context]).then(function(result) {
                self.current_period = result['period_id'];
                self.current_zone = result['zone_id'];
                self.current_day = result['dayNum'];
            }));

            defs.push(mod.call("list_zones", []).then(function(result) {
                self.zones = result;
            }));
            defs.push(mod.call("list_periods", []).then(function(result) {
                self.periods = result;
            }));
            defs.push(mod.call("list_days", []).then(function(result) {
                self.days = result;
            }));
            return $.when(tmp, defs);
        },
        do_search: function(domain, context, group_by) {
            var self = this;
            this.last_domain = domain;
            this.last_context = context;
            this.last_group_by = group_by;
            this.old_search = _.bind(this._super, this);
            var o;
            self.$el.parent().find('.oe_oschool_select_zone').children().remove().end();
            self.$el.parent().find('.oe_oschool_select_zone').append(new Option('', ''));
            for (var i = 0;i < self.zones.length;i++){
                o = new Option(self.zones[i][1], self.zones[i][0]);
                if (self.zones[i][0] === self.current_zone){
                    $(o).attr('selected',true);
                }
                self.$el.parent().find('.oe_oschool_select_zone').append(o);
            }

            self.$el.parent().find('.oe_oschool_select_period').children().remove().end();
            self.$el.parent().find('.oe_oschool_select_period').append(new Option('', ''));
            for (var i = 0;i < self.periods.length;i++){
                o = new Option(self.periods[i][1], self.periods[i][0]);
                if (self.periods[i][0] === self.current_period){
                    $(o).attr('selected',true);
                }
                self.$el.parent().find('.oe_oschool_select_period').append(o);
            }
            self.$el.parent().find('.oe_oschool_select_day').children().remove().end();
            self.$el.parent().find('.oe_oschool_select_day').append(new Option('', ''));
            for (var i = 0;i < self.days.length;i++){
                o = new Option(self.days[i][1], self.days[i][0]);
                if (self.days[i][0] === self.current_day){
                    $(o).attr('selected',true);
                }
                self.$el.parent().find('.oe_oschool_select_day').append(o);
            }

            return self.search_by_zone_period_day();
        },
        search_by_zone_period_day: function() {
            var self = this;
            var domain = [];
            if (self.current_zone !== null) domain.push(["zone_id", "=", self.current_zone]);
            self.last_context["zone_id"] = self.current_zone === null ? false : self.current_zone;

            if (self.current_period !== null) domain.push(["period_id", "=", self.current_period]);

            if (self.current_period === null) delete self.last_context["period_id"];
            else self.last_context["period_id"] =  self.current_period;

            if (self.current_day !== null) domain.push(["dayNum", "=", self.current_day]);

            if (self.current_day === null) delete self.last_context["dayNum"];
            else self.last_context["dayNum"] =  self.current_day;

            var compound_domain = new instance.web.CompoundDomain(self.last_domain, domain);
            self.dataset.domain = compound_domain.eval();
            return self.old_search(compound_domain, self.last_context, self.last_group_by);
        },
    });

    instance.web.views.add('tree_oschool_restaurant_presence_quickadd', 'instance.web.oschool.Restaurant');
    instance.web.oschool.Restaurant = instance.web.ListView.extend({
        init: function() {
            this._super.apply(this, arguments);
            this.classes = [];
            this.current_class = null;
            this.default_class = null;

            this.periods = [];
            this.current_period = null;
            this.default_period = null;

            this.days = [];
            this.current_day = null;
            this.default_day = null;

        },
        start:function(){
            var tmp = this._super.apply(this, arguments);
            var self = this;
            var defs = [];
            this.$el.parent().prepend(QWeb.render("OschoolServicePresenceQuickAdd", {widget: this}));

            this.$el.parent().find('.oe_oschool_select_class').change(function() {
                    self.current_class = this.value === '' ? null : parseInt(this.value);
                    self.do_search(self.last_domain, self.last_context, self.last_group_by);
                });

            this.$el.parent().find('.oe_oschool_select_period').change(function() {
                self.current_period = this.value === '' ? null : parseInt(this.value);
                self.do_search(self.last_domain, self.last_context, self.last_group_by);
            });
            this.$el.parent().find('.oe_oschool_print').click(function() {
                if(self.current_period == null
                    || self.current_period == ''
                    || self.current_class == null
                    || self.current_class == '')
                {
                    alert( "Choose the period and the class first!" );
                }else{
                    defs.push(mod.call("print_report", [self.current_period, self.current_class]).then(function(result) {
                        self.do_action(result);
                    }));
                }
            });
            this.$el.parent().find('.oe_oschool_select_day').change(function() {
                self.current_day = this.value === '' ? null : parseInt(this.value);
                self.do_search(self.last_domain, self.last_context, self.last_group_by);
            });
            this.on('edit:after', this, function () {
                self.$el.parent().find('.oe_oschool_select_class').attr('disabled', 'disabled');
                self.$el.parent().find('.oe_oschool_select_period').attr('disabled', 'disabled');
                self.$el.parent().find('.oe_oschool_select_day').attr('disabled', 'disabled');
                //self.$el.parent().find('.oe_oschool_select_category').attr('disabled', 'disabled');
            });
            this.on('save:after cancel:after', this, function () {
                self.$el.parent().find('.oe_oschool_select_class').removeAttr('disabled');
                self.$el.parent().find('.oe_oschool_select_period').removeAttr('disabled');
                self.$el.parent().find('.oe_oschool_select_day').removeAttr('disabled');
                //self.$el.parent().find('.oe_oschool_select_category').removeAttr('disabled');
            });
            var mod = new instance.web.Model("oschool.student_restaurant_presence", self.dataset.context, self.dataset.domain);

            defs.push(mod.call("default_get", [['class_id','period_id','day_num'],self.dataset.context]).then(function(result) {
                self.current_period = result['period_id'];
                self.current_class = result['class_id'];
                self.current_day = result['day_num'];

            }));

            defs.push(mod.call("list_classes", []).then(function(result) {
                self.classes = result;
            }));
            defs.push(mod.call("list_periods", []).then(function(result) {
                self.periods = result;
            }));
            defs.push(mod.call("list_days", []).then(function(result) {
                self.days = result;
            }));

            return $.when(tmp, defs);
        },
        do_search: function(domain, context, group_by) {
            var self = this;
            this.last_domain = domain;
            this.last_context = context;
            this.last_group_by = group_by;
            this.old_search = _.bind(this._super, this);
            var o;
            self.$el.parent().find('.oe_oschool_select_class').children().remove().end();
            self.$el.parent().find('.oe_oschool_select_class').append(new Option('', ''));
            for (var i = 0;i < self.classes.length;i++){
                o = new Option(self.classes[i][1], self.classes[i][0]);
                if (self.classes[i][0] === self.current_class){
                    $(o).attr('selected',true);
                }
                self.$el.parent().find('.oe_oschool_select_class').append(o);
            }

            self.$el.parent().find('.oe_oschool_select_period').children().remove().end();
            self.$el.parent().find('.oe_oschool_select_period').append(new Option('', ''));
            for (var i = 0;i < self.periods.length;i++){
                o = new Option(self.periods[i][1], self.periods[i][0]);
                if (self.periods[i][0] === self.current_period){
                    $(o).attr('selected',true);
                }
                self.$el.parent().find('.oe_oschool_select_period').append(o);
            }
            self.$el.parent().find('.oe_oschool_select_day').children().remove().end();
            self.$el.parent().find('.oe_oschool_select_day').append(new Option('', ''));
            for (var i = 0;i < self.days.length;i++){
                o = new Option(self.days[i][1], self.days[i][0]);
                if (self.days[i][0] === self.current_day){
                    $(o).attr('selected',true);
                }
                self.$el.parent().find('.oe_oschool_select_day').append(o);
            }

            return self.search_by_class_period_category();
        },
        search_by_class_period_category: function() {
            var self = this;
            var domain = [];
            if (self.current_class !== null) domain.push(["class_id", "=", self.current_class]);
            self.last_context["class_id"] = self.current_class === null ? false : self.current_class;

            if (self.current_period !== null) domain.push(["period_id", "=", self.current_period]);

            if (self.current_period === null) delete self.last_context["period_id"];
            else self.last_context["period_id"] =  self.current_period;

            if (self.current_day !== null) domain.push(["day_num", "=", self.current_day]);

            if (self.current_day === null) delete self.last_context["day_num"];
            else self.last_context["day_num"] =  self.current_day;

            var compound_domain = new instance.web.CompoundDomain(self.last_domain, domain);
            self.dataset.domain = compound_domain.eval();
            return self.old_search(compound_domain, self.last_context, self.last_group_by);
        },
    });
    instance.web.views.add('tree_oschool_canteen_presence_quickadd', 'instance.web.oschool.Canteeen');
    instance.web.oschool.Canteeen = instance.web.ListView.extend({
        init: function() {
            this._super.apply(this, arguments);
            this.classes = [];
            this.current_class = null;
            this.default_class = null;

            this.periods = [];
            this.current_period = null;
            this.default_period = null;

            this.days = [];
            this.current_day = null;
            this.default_day = null;

            this.categories = [];
            this.current_category = null;
            this.default_category = null;
        },
        start:function(){
            var tmp = this._super.apply(this, arguments);
            var self = this;
            var defs = [];
            this.$el.parent().prepend(QWeb.render("OschoolServicePresenceQuickAdd", {widget: this}));

            this.$el.parent().find('.oe_oschool_select_class').change(function() {
                    self.current_class = this.value === '' ? null : parseInt(this.value);
                    self.do_search(self.last_domain, self.last_context, self.last_group_by);
                });

            this.$el.parent().find('.oe_oschool_select_period').change(function() {
                self.current_period = this.value === '' ? null : parseInt(this.value);
                self.do_search(self.last_domain, self.last_context, self.last_group_by);
            });

            this.$el.parent().find('.oe_oschool_print').click(function() {
                if(self.current_period == null
                    || self.current_period == ''
                    || self.current_class == null
                    || self.current_class == '')
                {
                    alert( "Choose the period and the class first!" );
                }else{
                    defs.push(mod.call("print_report", [self.current_period, self.current_class]).then(function(result) {
                        self.do_action(result);
                    }));
                }
            });

            this.$el.parent().find('.oe_oschool_select_day').change(function() {
                self.current_day = this.value === '' ? null : parseInt(this.value);
                self.do_search(self.last_domain, self.last_context, self.last_group_by);
            });
            this.on('edit:after', this, function () {
                self.$el.parent().find('.oe_oschool_select_class').attr('disabled', 'disabled');
                self.$el.parent().find('.oe_oschool_select_period').attr('disabled', 'disabled');
                self.$el.parent().find('.oe_oschool_select_day').attr('disabled', 'disabled');
                //self.$el.parent().find('.oe_oschool_select_category').attr('disabled', 'disabled');
            });
            this.on('save:after cancel:after', this, function () {
                self.$el.parent().find('.oe_oschool_select_class').removeAttr('disabled');
                self.$el.parent().find('.oe_oschool_select_period').removeAttr('disabled');
                self.$el.parent().find('.oe_oschool_select_day').removeAttr('disabled');
                //self.$el.parent().find('.oe_oschool_select_category').removeAttr('disabled');
            });
            var mod = new instance.web.Model("oschool.student_canteen_presence", self.dataset.context, self.dataset.domain);
            var mod2 = new instance.web.Model("oschool.student_restaurant_presence", self.dataset.context, self.dataset.domain);

            defs.push(mod.call("default_get", [['class_id','period_id','day_num'],self.dataset.context]).then(function(result) {
                self.current_period = result['period_id'];
                self.current_class = result['class_id'];
                self.current_day = result['day_num'];
            }));

            defs.push(mod2.call("list_classes", []).then(function(result) {
                self.classes = result;
            }));
            defs.push(mod2.call("list_periods", []).then(function(result) {
                self.periods = result;
            }));
            defs.push(mod2.call("list_days", []).then(function(result) {
                self.days = result;
            }));

            return $.when(tmp, defs);
        },
        do_search: function(domain, context, group_by) {
            var self = this;
            this.last_domain = domain;
            this.last_context = context;
            this.last_group_by = group_by;
            this.old_search = _.bind(this._super, this);
            var o;
            self.$el.parent().find('.oe_oschool_select_class').children().remove().end();
            self.$el.parent().find('.oe_oschool_select_class').append(new Option('', ''));
            for (var i = 0;i < self.classes.length;i++){
                o = new Option(self.classes[i][1], self.classes[i][0]);
                if (self.classes[i][0] === self.current_class){
                    $(o).attr('selected',true);
                }
                self.$el.parent().find('.oe_oschool_select_class').append(o);
            }

            self.$el.parent().find('.oe_oschool_select_period').children().remove().end();
            self.$el.parent().find('.oe_oschool_select_period').append(new Option('', ''));
            for (var i = 0;i < self.periods.length;i++){
                o = new Option(self.periods[i][1], self.periods[i][0]);
                if (self.periods[i][0] === self.current_period){
                    $(o).attr('selected',true);
                }
                self.$el.parent().find('.oe_oschool_select_period').append(o);
            }
            self.$el.parent().find('.oe_oschool_select_day').children().remove().end();
            self.$el.parent().find('.oe_oschool_select_day').append(new Option('', ''));
            for (var i = 0;i < self.days.length;i++){
                o = new Option(self.days[i][1], self.days[i][0]);
                if (self.days[i][0] === self.current_day){
                    $(o).attr('selected',true);
                }
                self.$el.parent().find('.oe_oschool_select_day').append(o);
            }

            return self.search_by_class_period_category();
        },
        search_by_class_period_category: function() {
            var self = this;
            var domain = [];
            if (self.current_class !== null) domain.push(["class_id", "=", self.current_class]);
            self.last_context["class_id"] = self.current_class === null ? false : self.current_class;

            if (self.current_period !== null) domain.push(["period_id", "=", self.current_period]);

            if (self.current_period === null) delete self.last_context["period_id"];
            else self.last_context["period_id"] =  self.current_period;

            if (self.current_day !== null) domain.push(["day_num", "=", self.current_day]);

            if (self.current_day === null) delete self.last_context["day_num"];
            else self.last_context["day_num"] =  self.current_day;

            var compound_domain = new instance.web.CompoundDomain(self.last_domain, domain);
            self.dataset.domain = compound_domain.eval();
            return self.old_search(compound_domain, self.last_context, self.last_group_by);
        },
    });
    instance.web.views.add('tree_oschool_ticket_presence_quickadd', 'instance.web.oschool.Ticket');
    instance.web.oschool.Ticket = instance.web.ListView.extend({
        init: function() {
            this._super.apply(this, arguments);
            this.classes = [];
            this.current_class = null;
            this.default_class = null;

            this.periods = [];
            this.current_period = null;
            this.default_period = null;

            this.days = [];
            this.current_day = null;
            this.default_day = null;

            this.categories = [];
            this.current_category = null;
            this.default_category = null;
        },
        start:function(){
            var tmp = this._super.apply(this, arguments);
            var self = this;
            var defs = [];
            this.$el.parent().prepend(QWeb.render("OschoolServicePresenceQuickAdd", {widget: this}));

            this.$el.parent().find('.oe_oschool_select_class').change(function() {
                    self.current_class = this.value === '' ? null : parseInt(this.value);
                    self.do_search(self.last_domain, self.last_context, self.last_group_by);
                });

            this.$el.parent().find('.oe_oschool_select_period').change(function() {
                self.current_period = this.value === '' ? null : parseInt(this.value);
                self.do_search(self.last_domain, self.last_context, self.last_group_by);
            });

            this.$el.parent().find('.oe_oschool_print').click(function() {
                if(self.current_period == null
                    || self.current_period == ''
                    || self.current_class == null
                    || self.current_class == '')
                {
                    alert( "Choose the period and the class first!" );
                }else{
                    defs.push(mod.call("print_report", [self.current_period, self.current_class]).then(function(result) {
                        self.do_action(result);
                    }));
                }
            });

            this.$el.parent().find('.oe_oschool_select_day').change(function() {
                self.current_day = this.value === '' ? null : parseInt(this.value);
                self.do_search(self.last_domain, self.last_context, self.last_group_by);
            });
            this.on('edit:after', this, function () {
                self.$el.parent().find('.oe_oschool_select_class').attr('disabled', 'disabled');
                self.$el.parent().find('.oe_oschool_select_period').attr('disabled', 'disabled');
                self.$el.parent().find('.oe_oschool_select_day').attr('disabled', 'disabled');
                //self.$el.parent().find('.oe_oschool_select_category').attr('disabled', 'disabled');
            });
            this.on('save:after cancel:after', this, function () {
                self.$el.parent().find('.oe_oschool_select_class').removeAttr('disabled');
                self.$el.parent().find('.oe_oschool_select_period').removeAttr('disabled');
                self.$el.parent().find('.oe_oschool_select_day').removeAttr('disabled');
                //self.$el.parent().find('.oe_oschool_select_category').removeAttr('disabled');
            });
            var mod = new instance.web.Model("oschool.ticket_presence", self.dataset.context, self.dataset.domain);
            var mod2 = new instance.web.Model("oschool.student_restaurant_presence", self.dataset.context, self.dataset.domain);

            defs.push(mod.call("default_get", [['class_id','period_id','day_num'],self.dataset.context]).then(function(result) {
                self.current_period = result['period_id'];
                self.current_class = result['class_id'];
                self.current_day = result['day_num'];
            }));

            defs.push(mod2.call("list_classes", []).then(function(result) {
                self.classes = result;
            }));
            defs.push(mod2.call("list_periods", []).then(function(result) {
                self.periods = result;
            }));
            defs.push(mod2.call("list_days", []).then(function(result) {
                self.days = result;
            }));

            return $.when(tmp, defs);
        },
        do_search: function(domain, context, group_by) {
            var self = this;
            this.last_domain = domain;
            this.last_context = context;
            this.last_group_by = group_by;
            this.old_search = _.bind(this._super, this);
            var o;
            self.$el.parent().find('.oe_oschool_select_class').children().remove().end();
            self.$el.parent().find('.oe_oschool_select_class').append(new Option('', ''));
            for (var i = 0;i < self.classes.length;i++){
                o = new Option(self.classes[i][1], self.classes[i][0]);
                if (self.classes[i][0] === self.current_class){
                    $(o).attr('selected',true);
                }
                self.$el.parent().find('.oe_oschool_select_class').append(o);
            }

            self.$el.parent().find('.oe_oschool_select_period').children().remove().end();
            self.$el.parent().find('.oe_oschool_select_period').append(new Option('', ''));
            for (var i = 0;i < self.periods.length;i++){
                o = new Option(self.periods[i][1], self.periods[i][0]);
                if (self.periods[i][0] === self.current_period){
                    $(o).attr('selected',true);
                }
                self.$el.parent().find('.oe_oschool_select_period').append(o);
            }
            self.$el.parent().find('.oe_oschool_select_day').children().remove().end();
            self.$el.parent().find('.oe_oschool_select_day').append(new Option('', ''));
            for (var i = 0;i < self.days.length;i++){
                o = new Option(self.days[i][1], self.days[i][0]);
                if (self.days[i][0] === self.current_day){
                    $(o).attr('selected',true);
                }
                self.$el.parent().find('.oe_oschool_select_day').append(o);
            }

            return self.search_by_class_period_category();
        },
        search_by_class_period_category: function() {
            var self = this;
            var domain = [];
            if (self.current_class !== null) domain.push(["class_id", "=", self.current_class]);
            self.last_context["class_id"] = self.current_class === null ? false : self.current_class;

            if (self.current_period !== null) domain.push(["period_id", "=", self.current_period]);

            if (self.current_period === null) delete self.last_context["period_id"];
            else self.last_context["period_id"] =  self.current_period;

            if (self.current_day !== null) domain.push(["day_num", "=", self.current_day]);

            if (self.current_day === null) delete self.last_context["day_num"];
            else self.last_context["day_num"] =  self.current_day;

            var compound_domain = new instance.web.CompoundDomain(self.last_domain, domain);
            self.dataset.domain = compound_domain.eval();
            return self.old_search(compound_domain, self.last_context, self.last_group_by);
        },
    });
    instance.web.views.add('tree_oschool_club_presence_quickadd', 'instance.web.oschool.Club');
    instance.web.oschool.Club = instance.web.ListView.extend({
        init: function() {
            this._super.apply(this, arguments);
            this.clubs = [];
            this.current_club = null;
            this.default_club = null;

            this.periods = [];
            this.current_period = null;
            this.default_period = null;

            this.days = [];
            this.current_day = null;
            this.default_day = null;

            this.categories = [];
            this.current_category = null;
            this.default_category = null;
        },
        start:function(){
            var tmp = this._super.apply(this, arguments);
            var self = this;
            var defs = [];
            this.$el.parent().prepend(QWeb.render("OschoolClubPresenceQuickAdd", {widget: this}));

            this.$el.parent().find('.oe_oschool_select_club').change(function() {
                    self.current_club = this.value === '' ? null : parseInt(this.value);
                    self.do_search(self.last_domain, self.last_context, self.last_group_by);
                });

            this.$el.parent().find('.oe_oschool_select_period').change(function() {
                self.current_period = this.value === '' ? null : parseInt(this.value);
                self.do_search(self.last_domain, self.last_context, self.last_group_by);
            });

            this.$el.parent().find('.oe_oschool_select_day').change(function() {
                self.current_day = this.value === '' ? null : parseInt(this.value);
                self.do_search(self.last_domain, self.last_context, self.last_group_by);
            });
            this.on('edit:after', this, function () {
                self.$el.parent().find('.oe_oschool_select_club').attr('disabled', 'disabled');
                self.$el.parent().find('.oe_oschool_select_period').attr('disabled', 'disabled');
                self.$el.parent().find('.oe_oschool_select_day').attr('disabled', 'disabled');
            });
            this.on('save:after cancel:after', this, function () {
                self.$el.parent().find('.oe_oschool_select_club').removeAttr('disabled');
                self.$el.parent().find('.oe_oschool_select_period').removeAttr('disabled');
                self.$el.parent().find('.oe_oschool_select_day').removeAttr('disabled');
            });
            var mod = new instance.web.Model("oschool.student_club_presence", self.dataset.context, self.dataset.domain);

            defs.push(mod.call("default_get", [['club_id','period_id','day_num'],self.dataset.context]).then(function(result) {
                self.current_period = result['period_id'];
                self.current_club = result['club_id'];
                self.current_day = result['day_num'];
            }));

            defs.push(mod.call("get_list_clubs", []).then(function(result) {
                self.clubs = result;
            }));
            defs.push(mod.call("get_list_periods", []).then(function(result) {
                self.periods = result;
            }));
            defs.push(mod.call("get_list_days", []).then(function(result) {
                self.days = result;
            }));

            return $.when(tmp, defs);
        },
        do_search: function(domain, context, group_by) {
            var self = this;
            this.last_domain = domain;
            this.last_context = context;
            this.last_group_by = group_by;
            this.old_search = _.bind(this._super, this);
            var o;
            self.$el.parent().find('.oe_oschool_select_club').children().remove().end();
            self.$el.parent().find('.oe_oschool_select_club').append(new Option('', ''));
            for (var i = 0;i < self.clubs.length;i++){
                o = new Option(self.clubs[i][1], self.clubs[i][0]);
                if (self.clubs[i][0] === self.current_club){
                    $(o).attr('selected',true);
                }
                self.$el.parent().find('.oe_oschool_select_club').append(o);
            }

            self.$el.parent().find('.oe_oschool_select_period').children().remove().end();
            self.$el.parent().find('.oe_oschool_select_period').append(new Option('', ''));
            for (var i = 0;i < self.periods.length;i++){
                o = new Option(self.periods[i][1], self.periods[i][0]);
                if (self.periods[i][0] === self.current_period){
                    $(o).attr('selected',true);
                }
                self.$el.parent().find('.oe_oschool_select_period').append(o);
            }
            self.$el.parent().find('.oe_oschool_select_day').children().remove().end();
            self.$el.parent().find('.oe_oschool_select_day').append(new Option('', ''));
            for (var i = 0;i < self.days.length;i++){
                o = new Option(self.days[i][1], self.days[i][0]);
                if (self.days[i][0] === self.current_day){
                    $(o).attr('selected',true);
                }
                self.$el.parent().find('.oe_oschool_select_day').append(o);
            }

            return self.search_by_club_period_day();
        },
        search_by_club_period_day: function() {
            var self = this;
            var domain = [];
            if (self.current_club !== null) domain.push(["club_id", "=", self.current_club]);
            self.last_context["club_id"] = self.current_club === null ? false : self.current_club;

            if (self.current_period !== null) domain.push(["period_id", "=", self.current_period]);

            if (self.current_period === null) delete self.last_context["period_id"];
            else self.last_context["period_id"] =  self.current_period;

            if (self.current_day !== null) domain.push(["day_num", "=", self.current_day]);

            if (self.current_day === null) delete self.last_context["day_num"];
            else self.last_context["day_num"] =  self.current_day;

            var compound_domain = new instance.web.CompoundDomain(self.last_domain, domain);
            self.dataset.domain = compound_domain.eval();
            return self.old_search(compound_domain, self.last_context, self.last_group_by);
        },
    });

};
