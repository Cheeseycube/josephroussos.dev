$('#graphOptions').on('change',function(){
    
    $.ajax({
        url: "/change_graph",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: {
            'selected': document.querySelector('input[name=select_graph]:checked').value

        },
        dataType:"json",
        success: function (data) {
            Plotly.newPlot('committed_sankey_diagram', data );
        }
    });
})