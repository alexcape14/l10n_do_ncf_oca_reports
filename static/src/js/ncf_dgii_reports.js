odoo.define('l10n_do_ncf_oca_reports.widgets', function (require) {
    "use strict";

    var form_common = require('web.form_common');
    var core = require('web.core');

    var Copyright = form_common.FormWidget.extend(form_common.ReinitializeWidgetMixin, {
        start: function () {
            this.$el.append("<a href='https://github.com/odoo-dominicana' target='_blank'>&#169; Marcos Organizador de Negocios SRL / SoftNet Team SRL / ODOO Dominicana</a>");
        }
    });

    core.form_custom_registry.add("opl", Copyright);

});