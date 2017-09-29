$(document).ready(function(){

     $.ajax({
          url:'/home-images',
          type:'GET',
          dataType:'json',
          success:function(data){
            var x = [];
            for(var i=0;i<data.length;i++){
                x.push('/static/img/' + data[i]['img_name']);

            }
            $('#demo').backstretch(x,{duration:5000,fade:750});

          }


    });

});
