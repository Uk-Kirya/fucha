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
    var owl = $('.categories');
    var rowCount = 3; // Количество рядов

    owl.owlCarousel({
        margin: 0,
        nav: false,
        dots: false, // Отключаем стандартные точки
        autoHeight: true,
        loop: false,
        items: 1.1,
        owl2row: true,
        owl2rowCount: rowCount
    });

    // Создаем кастомные точки
    function createCustomDots() {
        var itemsCount = owl.find('.owl2row-item').length;
        var dotsContainer = $('<div class="owl-dots custom-dots"></div>');

        for (var i = 0; i < itemsCount; i++) {
            var dot = $('<button role="button" class="owl-dot"></button>');
            if (i === 0) dot.addClass('active');
            dot.data('index', i);
            dotsContainer.append(dot);
        }

        $('.categories').append(dotsContainer);

        // Обработчик клика
        dotsContainer.find('.owl-dot').on('click', function() {
            var index = $(this).data('index');
            owl.trigger('to.owl.carousel', [index, 300]);
        });
    }

    // Обновляем активную точку при смене слайда
    owl.on('changed.owl.carousel', function(event) {
        var currentIndex = event.item.index;
        $('.categories .owl-dot').removeClass('active');
        $('.categories .owl-dot').each(function() {
            if ($(this).data('index') === currentIndex) {
                $(this).addClass('active');
            }
        });
    });

    // Ждем инициализации и создаем точки
    setTimeout(createCustomDots, 100);
});


/**
 * Owl2row
 * @since 2.0.2
 */
; (function ($, window, document, undefined) {
    Owl2row = function (scope) {
        this.owl = scope;
        this.owl.options = $.extend({}, Owl2row.Defaults, this.owl.options);

        this.handlers = {
            'initialize.owl.carousel': $.proxy(function (e) {
                if (this.owl.settings.owl2row) {
                    this.build2row(this);
                    this.updateDotsAndNav(this);
                }
            }, this),
            'changed.owl.carousel': $.proxy(function (e) {
                if (this.owl.settings.owl2row) {
                    this.updateActiveStates(this);
                }
            }, this),
            'resize.owl.carousel': $.proxy(function (e) {
                if (this.owl.settings.owl2row) {
                    this.updateDotsAndNav(this);
                }
            }, this)
        };

        this.owl.$element.on(this.handlers);
    };

    Owl2row.Defaults = {
        owl2row: false,
        owl2rowCount: 2,
        owl2rowTarget: 'item',
        owl2rowContainer: 'owl2row-item',
        owl2rowDirection: 'ltr'
    };

    Owl2row.prototype.build2row = function (thisScope) {
        var carousel = $(thisScope.owl.$element);
        var carouselItems = carousel.find('.' + thisScope.owl.options.owl2rowTarget);
        var rowsCount = thisScope.owl.options.owl2rowCount;

        var items = [];
        $.each(carouselItems, function (index, item) {
            items.push(item);
        });

        carousel.find('.' + thisScope.owl.options.owl2rowContainer).remove();

        var itemsPerRow = Math.ceil(items.length / rowsCount);

        for (var i = 0; i < itemsPerRow; i++) {
            var rowContainer = $('<div class="' + thisScope.owl.options.owl2rowContainer + '"/>');

            for (var j = 0; j < rowsCount; j++) {
                var index = j * itemsPerRow + i;
                if (index < items.length) {
                    items[index].style.marginBottom = thisScope.owl.options.margin + 'px';
                    rowContainer.append(items[index]);
                }
            }

            carousel.append(rowContainer);
        }

        // Обновляем внутреннее состояние
        var newItems = carousel.find('.' + thisScope.owl.options.owl2rowContainer);
        thisScope.owl._items = newItems;
        thisScope.owl._itemsCount = newItems.length;

        // Обновляем навигацию
        if (thisScope.owl._itemsCount <= 1) {
            thisScope.owl._navText = ['', ''];
        }
    };

    Owl2row.prototype.updateDotsAndNav = function (thisScope) {
        var itemsCount = thisScope.owl._itemsCount;

        // Обновляем точки
        var dotsContainer = thisScope.owl.$element.find('.owl-dots');
        if (dotsContainer.length) {
            dotsContainer.empty();
            for (var i = 0; i < itemsCount; i++) {
                var dot = $('<button role="button" class="owl-dot"></button>');
                if (i === 0) dot.addClass('active');
                dot.data('index', i);
                dotsContainer.append(dot);
            }

            dotsContainer.find('.owl-dot').off('click').on('click', function() {
                var index = $(this).data('index');
                thisScope.owl.to(index, 300);
            });
        }

        // Обновляем навигацию (nav)
        thisScope.updateNavVisibility(thisScope);
    };

    Owl2row.prototype.updateNavVisibility = function (thisScope) {
        var itemsCount = thisScope.owl._itemsCount;
        var currentIndex = thisScope.owl.current() || 0;

        var navPrev = thisScope.owl.$element.find('.owl-prev');
        var navNext = thisScope.owl.$element.find('.owl-next');

        if (thisScope.owl.settings.loop) {
            navPrev.show();
            navNext.show();
            return;
        }

        // Для loop: false
        if (currentIndex <= 0) {
            navPrev.hide();
        } else {
            navPrev.show();
        }

        if (currentIndex >= itemsCount - 1) {
            navNext.hide();
        } else {
            navNext.show();
        }
    };

    Owl2row.prototype.updateActiveStates = function (thisScope) {
        var currentIndex = thisScope.owl.current();
        var itemsCount = thisScope.owl._itemsCount;

        // Обновляем точки
        var dots = thisScope.owl.$element.find('.owl-dot');
        dots.removeClass('active');
        if (dots.length > currentIndex) {
            $(dots[currentIndex]).addClass('active');
        }

        // Обновляем навигацию
        thisScope.updateNavVisibility(thisScope);
    };

    Owl2row.prototype.destroy = function () {
        var handler, property;
        for (handler in this.handlers) {
            this.owl.$element.off(handler, this.handlers[handler]);
        }
        for (property in Object.getOwnPropertyNames(this)) {
            typeof this[property] !== 'function' && (this[property] = null);
        }
    };

    $.fn.owlCarousel.Constructor.Plugins['owl2row'] = Owl2row;
})(window.Zepto || window.jQuery, window, document);

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.challenge__big__card__text__indicator span[data-percent]').forEach(el => {
        const percent = el.dataset.percent;
        el.style.setProperty('--percent', percent);
    });

    const categoryButtons = document.querySelectorAll('.categories__tabs button');
    const cards = document.querySelectorAll('.challenge__big__card');

    function filterCards(categoryId) {
        cards.forEach(card => {
            const cardCategoryId = card.dataset.categoryId;

            if (categoryId === 'all' || cardCategoryId === categoryId) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    }

    categoryButtons.forEach(button => {
        button.addEventListener('click', function() {
            categoryButtons.forEach(btn => btn.classList.remove('active__category'));
            this.classList.add('active__category');

            const categoryId = this.dataset.categoryId;

            if (!categoryId) {
                filterCards('all');
            } else {
                filterCards(categoryId);
            }
        });
    });
});