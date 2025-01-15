/** @odoo-module **/

// import SystrayMenu from 'web.SystrayMenu';

// import Widget from 'web.Widget';
// var QWeb = core.qweb;
// const core = require('web.core');


import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const { Component, useState, onWillStart } = owl;

class AircallDialpad extends Component {
    setup() {
        super.setup();
        this.state = useState({ isVisible: false });
    }
    _onClick(ev) {
        this.state.isVisible = !this.state.isVisible;
    }
}
AircallDialpad.template = "cit_aircall_api_integration.AircallDialpad";
export const systrayItem = {
    Component: AircallDialpad,
};
registry.category("systray").add("Dialpad", systrayItem, { sequence: 5 });
