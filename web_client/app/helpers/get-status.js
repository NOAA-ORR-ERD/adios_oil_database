import { helper } from '@ember/component/helper';

export default helper(function getStatus([status]) {
    if(Array.isArray(status) && status.length){
        // status is not OK
        var bError = false;
        for (const st of status){
            if(st.charAt(0).toLowerCase() === 'e'){
                bError = true;
                break;
            }
        }
        return bError ? "Errors" : "Warnings";
    } else {
        // status is OK
        return "OK";
    }
});
