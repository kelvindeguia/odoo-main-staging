odoo.define('cs_portal_18.HealthStatusWidget', function (require) {
    'use strict';

    const FieldSelection = require('web.basic_fields').FieldSelection;
    const fieldRegistry = require('web.field_registry');

    if (!FieldSelection || !fieldRegistry) {
        console.error('Required modules not loaded: web.basic_fields, web.field_registry');
        return;
    }

    const HealthStatusWidget = FieldSelection.extend({
        className: 'o_health_status',
        _render: function () {
            this._super();
            const colorMap = {
                red: 'background-color: #ff0000;',
                orange: 'background-color: #ffa500;',
                green: 'background-color: #008000;',
            };
            const color = colorMap[this.value] || '';
            this.$el.html(`<span class="o_health_circle" style="${color}"></span>`);
        },
    });

    fieldRegistry.add('health_status_widget', HealthStatusWidget);

    console.log('HealthStatusWidget JS loaded successfully!');
    return HealthStatusWidget;
});