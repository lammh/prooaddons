openerp.oschool = function(instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    instance.web.oschool = instance.web.oschool || {};

    //local.HomePage = instance.Widget.extend({
    //    start: function() {
    //        this.$el.append(QWeb.render("HomePageTemplate"));
    //    },
    //});


    //instance.web.client_actions.add('club.homepage', 'instance.oschool.HomePage');
    instance.web.views.add('tree_transport_presence_quickadd', 'instance.web.oschool.QuickAddListView');

    instance.web.oschool.QuickAddListView = instance.web.ListView.extend({
        init: function() {
            this._super.apply(this, arguments);
            this.zones = [];
            this.groups = [];
            this.current_zone = null;
            this.current_group = null;
            this.default_zone = null;
            this.default_groupe = null;
            //this.current_zone_type = null;
            //this.current_zone_currency = null;
            //this.current_zone_analytic = null;
        },
        start:function(){
            var tmp = this._super.apply(this, arguments);
            var self = this;
            var defs = [];
            this.$el.parent().prepend(QWeb.render("OschoolTransportPresence", {widget: this}));
            this.$el.parent().find('.oe_account_select_zone').change(function() {
                    self.current_zone = this.value === '' ? null : parseInt(this.value);
                    self.do_search(self.last_domain, self.last_context, self.last_group_by);
                });
            var tmp = this._super.apply(this, arguments);
            var self = this;
            var defs = [];

            this.$el.parent().find('.oe_account_select_group').change(function() {
                    self.current_group = this.value === '' ? null : parseInt(this.value);
                    self.do_search(self.last_domain, self.last_context, self.last_group_by);
                });
            this.on('edit:after', this, function () {
                self.$el.parent().find('.oe_account_select_zone').attr('disabled', 'disabled');
                self.$el.parent().find('.oe_account_select_group').attr('disabled', 'disabled');
            });
            this.on('save:after cancel:after', this, function () {
                self.$el.parent().find('.oe_account_select_zone').removeAttr('disabled');
                self.$el.parent().find('.oe_account_select_group').removeAttr('disabled');
            });
            var mod = new instance.web.Model("oschool.student_transport_presence", self.dataset.context, self.dataset.domain);
            defs.push(mod.call("default_get", [['zone_id','group_id'],self.dataset.context]).then(function(result) {
                self.current_group = result['group_id'];
                self.current_zone = result['zone_id'];
            }));
            defs.push(mod.call("list_zones", []).then(function(result) {
                self.zones = result;
            }));
            defs.push(mod.call("list_groups", []).then(function(result) {
                self.groups = result;
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
            self.$el.parent().find('.oe_account_select_zone').children().remove().end();
            self.$el.parent().find('.oe_account_select_zone').append(new Option('', ''));
            for (var i = 0;i < self.zones.length;i++){
                o = new Option(self.zones[i][1], self.zones[i][0]);
                self.$el.parent().find('.oe_account_select_zone').append(o);
            }
            self.$el.parent().find('.oe_account_select_group').children().remove().end();
            self.$el.parent().find('.oe_account_select_group').append(new Option('', ''));
            for (var i = 0;i < self.groups.length;i++){
                o = new Option(self.groups[i][1], self.groups[i][0]);
                self.$el.parent().find('.oe_account_select_group').append(o);
            }
            self.$el.parent().find('.oe_account_select_group').val(self.current_group).attr('selected',true);
            return self.search_by_zone_group();
        },
        search_by_zone_group: function() {
            var self = this;
            var domain = [];
            if (self.current_zone !== null) domain.push(["zone_id", "=", self.current_zone]);
            if (self.current_group !== null) domain.push(["group_id", "=", self.current_group]);
            self.last_context["zone_id"] = self.current_zone === null ? false : self.current_zone;
            if (self.current_group === null) delete self.last_context["group_id"];
            else self.last_context["group_id"] =  self.current_group;
            var compound_domain = new instance.web.CompoundDomain(self.last_domain, domain);
            self.dataset.domain = compound_domain.eval();
            return self.old_search(compound_domain, self.last_context, self.last_group_by);
        },
    });
}
