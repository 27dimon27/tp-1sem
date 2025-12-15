(function () {
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function sendAjaxRequest(url, data, successCallback, errorCallback) {
        const csrftoken = getCookie('csrftoken');

        $.ajax({
            url: url,
            type: 'POST',
            data: data,
            headers: {
                'X-CSRFToken': csrftoken
            },
            dataType: 'json',
            success: successCallback,
            error: function (xhr, status, error) {
                console.error('AJAX Error:', error);
                if (errorCallback) errorCallback(xhr);
            }
        });
    }

    function checkAuth() {
        const $navbar = $('.navbar');
        return $navbar.text().indexOf('Log in') === -1 && $navbar.text().indexOf('Sign up') === -1;
    }

    $(document).on('click', '.question .like-btn, .question .dislike-btn', function (e) {
        e.preventDefault();

        const $btn = $(this);
        const $container = $btn.closest('.question');
        const questionId = $container.data('question-id');

        if (!questionId) return;

        if (!checkAuth()) {
            const loginUrl = '/login/?next=' + encodeURIComponent(window.location.pathname);
            window.location.href = loginUrl;
            return;
        }

        const isLikeBtn = $btn.hasClass('like-btn');
        const value = isLikeBtn ? 1 : -1;
        const $otherBtn = isLikeBtn ? $container.find('.dislike-btn') : $container.find('.like-btn');
        const $ratingValue = $container.find('.rating-value');

        $btn.css('transform', 'scale(0.9)');
        setTimeout(() => {
            $btn.css('transform', 'scale(1)');
        }, 150);

        sendAjaxRequest(
            '/ajax/like/question/',
            {
                question_id: questionId,
                value: value
            },
            function (response) {
                if (response.success) {
                    $ratingValue.text(response.new_rating);

                    if (response.action === 'added' || response.action === 'changed') {
                        $btn.addClass('active');
                        $otherBtn.removeClass('active');
                    } else if (response.action === 'removed') {
                        $btn.removeClass('active');
                        $otherBtn.removeClass('active');
                    }
                }
            },
            function (xhr) {
                if (xhr.status === 403) {
                    window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
                } else if (xhr.status === 400 && xhr.responseJSON && xhr.responseJSON.error) {
                    alert('Error: ' + xhr.responseJSON.error);
                }
            }
        );
    });

    $(document).on('click', '.question[data-question-id] .like-btn, .question[data-question-id] .dislike-btn', function (e) {
        e.preventDefault();

        const $btn = $(this);
        const $container = $btn.closest('.question[data-question-id]');
        const questionId = $container.data('question-id');

        if (!questionId) return;

        if (!checkAuth()) {
            const loginUrl = '/login/?next=' + encodeURIComponent(window.location.pathname);
            window.location.href = loginUrl;
            return;
        }

        const isLikeBtn = $btn.hasClass('like-btn');
        const value = isLikeBtn ? 1 : -1;
        const $otherBtn = isLikeBtn ? $container.find('.dislike-btn') : $container.find('.like-btn');
        const $ratingValue = $container.find('.rating-value');

        $btn.css('transform', 'scale(0.9)');
        setTimeout(() => {
            $btn.css('transform', 'scale(1)');
        }, 150);

        sendAjaxRequest(
            '/ajax/like/question/',
            {
                question_id: questionId,
                value: value
            },
            function (response) {
                if (response.success) {
                    $ratingValue.text(response.new_rating);

                    if (response.action === 'added' || response.action === 'changed') {
                        $btn.addClass('active');
                        $otherBtn.removeClass('active');
                    } else if (response.action === 'removed') {
                        $btn.removeClass('active');
                        $otherBtn.removeClass('active');
                    }
                }
            },
            function (xhr) {
                if (xhr.status === 403) {
                    window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
                } else if (xhr.status === 400 && xhr.responseJSON && xhr.responseJSON.error) {
                    alert('Error: ' + xhr.responseJSON.error);
                }
            }
        );
    });

    $(document).on('click', '.answer .like-btn, .answer .dislike-btn', function (e) {
        e.preventDefault();

        const $btn = $(this);
        const $container = $btn.closest('.answer');
        const answerId = $container.data('answer-id');

        if (!answerId) return;

        if (!checkAuth()) {
            const loginUrl = '/login/?next=' + encodeURIComponent(window.location.pathname);
            window.location.href = loginUrl;
            return;
        }

        const isLikeBtn = $btn.hasClass('like-btn');
        const value = isLikeBtn ? 1 : -1;
        const $otherBtn = isLikeBtn ? $container.find('.dislike-btn') : $container.find('.like-btn');
        const $ratingValue = $container.find('.rating-value');

        $btn.css('transform', 'scale(0.9)');
        setTimeout(() => {
            $btn.css('transform', 'scale(1)');
        }, 150);

        sendAjaxRequest(
            '/ajax/like/answer/',
            {
                answer_id: answerId,
                value: value
            },
            function (response) {
                if (response.success) {
                    $ratingValue.text(response.new_rating);

                    if (response.action === 'added' || response.action === 'changed') {
                        $btn.addClass('active');
                        $otherBtn.removeClass('active');
                    } else if (response.action === 'removed') {
                        $btn.removeClass('active');
                        $otherBtn.removeClass('active');
                    }
                }
            },
            function (xhr) {
                if (xhr.status === 403) {
                    window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
                } else if (xhr.status === 400 && xhr.responseJSON && xhr.responseJSON.error) {
                    alert('Error: ' + xhr.responseJSON.error);
                }
            }
        );
    });

    $(document).on('change', '.correct-checkbox input[type="checkbox"]', function () {
        const $checkbox = $(this);
        const $container = $checkbox.closest('.answer');
        const answerId = $container.data('answer-id');
        const isChecked = $checkbox.is(':checked');

        if (!checkAuth()) {
            const loginUrl = '/login/?next=' + encodeURIComponent(window.location.pathname);
            window.location.href = loginUrl;
            $checkbox.prop('checked', !isChecked);
            return;
        }

        sendAjaxRequest(
            '/ajax/mark-correct/',
            {
                answer_id: answerId,
                is_correct: isChecked
            },
            function (response) {
                if (response.success) {
                    if (isChecked) {
                        $container.addClass('correct');
                        $container.siblings('.answer').removeClass('correct')
                            .find('input[type="checkbox"]').prop('checked', false);
                    } else {
                        $container.removeClass('correct');
                    }
                } else {
                    $checkbox.prop('checked', !isChecked);
                    if (response.error) {
                        alert(response.error);
                    }
                }
            },
            function (xhr) {
                $checkbox.prop('checked', !isChecked);
                if (xhr.status === 403) {
                    alert('Only question author can mark correct answers');
                } else if (xhr.status === 400 && xhr.responseJSON && xhr.responseJSON.error) {
                    alert('Error: ' + xhr.responseJSON.error);
                }
            }
        );
    });

    $(document).ready(function () {
        if (!checkAuth()) {
            $('.like-btn, .dislike-btn, .correct-checkbox input[type="checkbox"]').each(function () {
                $(this).css('cursor', 'pointer');
            });
        }

        $('.like-btn, .dislike-btn').hover(
            function () {
                if (!checkAuth()) {
                    $(this).attr('title', 'Login to vote');
                }
            },
            function () {
                $(this).removeAttr('title');
            }
        );

        $('.correct-checkbox input[type="checkbox"]').hover(
            function () {
                if (!checkAuth()) {
                    $(this).attr('title', 'Login to mark correct answers');
                } else if ($(this).prop('disabled')) {
                    $(this).attr('title', 'Only question author can mark correct answers');
                }
            },
            function () {
                $(this).removeAttr('title');
            }
        );
    });
})();