axios.defaults.xsrfCookeName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

// Function to set Request Header with `CSRFTOKEN`
function setRequestHeader(){
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
}

function pay(amount, user, order) {
        var widget = new cp.CloudPayments();
        var csrftoken = getCookie('csrftoken');
        setRequestHeader();

        widget.pay('auth', // или 'charge'
            { //options
                publicId: 'test_api_00000000000000000000001', //id из личного кабинета
                description: 'Оплата товаров в example.com', //назначение
                amount: amount, //сумма
                currency: 'RUB', //валюта
                accountId: 'user@example.com', //идентификатор плательщика (необязательно)
                invoiceId: '1234567', //номер заказа  (необязательно)
                email: 'user@example.com', //email плательщика (необязательно)
                skin: "modern", //дизайн виджета (необязательно)
                data: {
                    myProp: 'myProp value'
                }
            },
                {
                    onSuccess: function (options) { // success
                    },
                    onFail: function (reason, options) { // fail
                        //действие при неуспешной оплате
                    },
                    onComplete: function (paymentResult, options) { //Вызывается как только виджет получает от api.cloudpayments ответ с результатом транзакции.
                        axios
                            .put(
                                '/extend-rent',
                                {
                                    'order': order,
                                    'user': user,
                                },
                                {
                                    headers:{
                                        'X-CSRFToken': csrftoken,
                                    }
                                }
                            ).then(window.location.reload());

                    }
                }
            )
}
