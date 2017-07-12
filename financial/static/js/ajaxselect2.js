/**
 * Created by kelvin on 6/28/2017.
 */
function ajaxselect2(table, customid){

    url = "/utils/ajaxselect/";
    toCall = customid != null ? $('#'+customid) : $('.ajaxselect2');

    toCall.select2({
        placeholder: "Enter keyword here...",
        ajax: {
            url: url,
            dataType: 'json',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term,
                    page: params.page || 1,
                    table: table
                };
            },
            processResults: function (data, params) {
                params.page = params.page || 1;

                return {
                    results: data.items,
                    pagination: {
                        more: true
                    }
                };
            }
        },
        escapeMarkup: function (markup) { return markup; },
        formatResult: function (data, term) {
            return data;
        },
        formatSelection: function (data) {
            return data;
        },
        minimumInputLength: 1
    });
}