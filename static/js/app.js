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

            var images =$.map(data,function(i) {return i.img_name; });
            $('#background-slideshow').backstretch(x,{duration:5000,fade:750});
            $(window).on("backstretch.show", function(e, instance) {
              var newCaption = data[instance.index].img_caption;
              $(".caption").html( newCaption );
            });



          }


    });

});
