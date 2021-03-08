<script>
$('.reserve-button').click(function(){


var selctddate = $(this).data('sdate');
    $.ajax
    ({
        url: 'reservebook.php',
        data: {"date": selctddate},
        type: 'post',
        success: function(result)
        {
          console.log(result);
        }
    });
});
</script>
