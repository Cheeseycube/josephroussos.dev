$('#graphOptions').on('change',function(){

    $.ajax({
        url: "/loading",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: {
            'selected': document.querySelector('button[name=Submit]:on').value

        },
        dataType:"json",
        success: function (data) {
            Plotly.newPlot('Backlog sankey', data );
        }
    });
})