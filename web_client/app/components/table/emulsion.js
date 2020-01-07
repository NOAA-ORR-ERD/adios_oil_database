import Component from '@ember/component';

export default Component.extend({
    didReceiveAttrs() {
        this._super(...arguments);

        this.set('tableFieldAttrs', {
            visual_stability: {
                label: 'Visual Stability',
                unitValue: false
            },
            water_content: {
                label: 'Water Content',
                unitValue: true
            },
            complex_viscosity: {
                label: 'Complex Viscosity',
                unitValue: true
            },
            complex_modulus: {
                label: 'Complex Modulus',
                unitValue: true
            },
            storage_modulus: {
                label: 'Storage Modulus',
                unitValue: true
            },
            loss_modulus: {
                label: 'Loss Modulus',
                unitValue: true
            },
            tan_delta_v_e: {
                label: 'Tan Delta (V/E)',
                unitValue: false
            },
            age: {
                label: 'Age',
                unitValue: true,
                convertUnit: 'days'
            },
            ref_temp: {
                label: 'Temperature',
                unitValue: true,
                convertUnit: 'C'
            }
        });
    }
});
