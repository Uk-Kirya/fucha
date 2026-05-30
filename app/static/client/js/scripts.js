$(".phone__mask").mask("+7 (999) 999 - 99 - 99");

(function () {
    'use strict'
    var forms = document.querySelectorAll('.needs-validation')

    Array.prototype.slice.call(forms)
        .forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (!form.checkValidity()) {
                    event.preventDefault()
                    event.stopPropagation()
                }

                form.classList.add('was-validated')
            }, false)
        })
})()


$(document).ready(function () {
    var owl = $('.slider');
    owl.owlCarousel({
        margin: 0,
        nav: true,
        dots: false,
        autoHeight: true,
        loop: true,
        items: 1
    });
})


$(document).ready(function () {
    var owl = $('.popular');
    owl.owlCarousel({
        margin: 24,
        nav: true,
        dots: false,
        autoHeight: true,
        loop: true,
        responsive: {
            0: {
              items: 2
            },
            576: {
              items: 2
            },
            768: {
              items: 3
            },
            1200: {
              items: 4
            }
          }
    });
})


$(document).ready(function () {
    $("a.topLink").click(function () {
        $("html, body").animate({
            scrollTop: $($(this).attr("href")).offset().top + "px"
        }, {
            duration: 0,
            easing: "swing"
        });
        return false;
    });
});


$(function () {
    $(window).scroll(function () {
        var top = $(document).scrollTop();
        if (top > 40) $('.head').addClass('head_fixed');
        else $('.head').removeClass('head_fixed');
    });
});


AOS.init({
    duration: 1500,
    offset: 0,
    once: false
});