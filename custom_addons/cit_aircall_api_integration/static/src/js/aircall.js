/** @odoo-module **/
import AircallPhone from '@cit_aircall_api_integration/js/aircallPhone';
import { PhoneField } from "@web/views/fields/phone/phone_field";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";

const phone = new AircallPhone({
    domToLoadPhone: '#phone',
    onLogin: settings => {
        console.log('phone loaded', settings);
    },
    onLogout: () => {
        console.log('phone logout');
        setPhoneVisibility(false);
    }
});

const setPhoneVisibility = visible => {
    const phoneContainer = document.querySelector('.iframe_dialpad');
    if (phoneContainer) {
        if (visible) {
            phoneContainer.classList.remove('d-none');
        } else {
            phoneContainer.classList.add('d-none');
        }
    }
};

phone.on('incoming_call', callInfos => {
    setPhoneVisibility(true);
});

patch(PhoneField.prototype, {
    /**
     * Called when the phone number is clicked.
     *
     * @private
     * @param {MouseEvent} ev
     */
    onClickCall(ev) {
        if (this.props.record._textValues.phone && ev.currentTarget.classList.contains('o_phone_form_link')) {
            const payload = {
                phone_number: this.props.record._textValues[this.props.name]
            };
            phone.send(
                'dial_number',
                payload,
                (success, data) => {
                    setPhoneVisibility(true);
                    console.log('success of dial: ', success);
                    console.log('success data: ', data);
                }
            );
        }
    },
});
