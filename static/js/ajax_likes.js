(function () {
    let activeRequest = false;

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

    function sendAjaxRequest(url, data, successCallback, errorCallback, options = {}) {
        const csrftoken = getCookie('csrftoken');

        return $.ajax({
            url: url,
            type: 'POST',
            data: data,
            headers: {
                'X-CSRFToken': csrftoken
            },
            dataType: 'json',
            success: successCallback,
            error: function (xhr) {
                if (errorCallback) errorCallback(xhr);
            },
            ...options
        });
    }

    function checkAuth() {
        const $navbar = $('.navbar');
        return $navbar.text().indexOf('Log in') === -1 && $navbar.text().indexOf('Sign up') === -1;
    }

    function handleLike($btn, entityType, entityId) {
        const isOwnContent = $btn.data('own') === 'true' || $btn.hasClass('disabled-own');
        if (isOwnContent) {
            return false;
        }

        if (activeRequest) {
            return false;
        }

        if (!checkAuth()) {
            const loginUrl = '/login/?next=' + encodeURIComponent(window.location.pathname);
            window.location.href = loginUrl;
            return false;
        }

        const isLikeBtn = $btn.hasClass('like-btn');
        const value = isLikeBtn ? 1 : -1;
        const $container = $btn.closest('.question, .answer');
        const $otherBtn = isLikeBtn ? $container.find('.dislike-btn') : $container.find('.like-btn');
        const $ratingValue = $container.find('.rating-value');

        const isOtherOwnContent = $otherBtn.data('own') === 'true' || $otherBtn.hasClass('disabled-own');
        if (isOtherOwnContent) {
            return false;
        }

        const oldRating = parseInt($ratingValue.text()) || 0;
        const wasActive = $btn.hasClass('active');
        const otherWasActive = $otherBtn.hasClass('active');

        let newRating = oldRating;
        
        if (wasActive) {
            newRating -= value;
        } else {
            if (otherWasActive) {
                newRating = oldRating + (value * 2);
            } else {
                newRating = oldRating + value;
            }
        }
        
        $ratingValue.text(newRating);
        if (wasActive) {
            $btn.removeClass('active');
        } else {
            $btn.addClass('active');
            $otherBtn.removeClass('active');
        }

        activeRequest = true;
        $btn.prop('disabled', true);
        $otherBtn.prop('disabled', true);
        $btn.css('cursor', 'wait');
        $otherBtn.css('cursor', 'wait');

        $btn.css('transform', 'scale(0.9)');
        setTimeout(() => {
            $btn.css('transform', 'scale(1)');
        }, 150);

        const url = entityType === 'question' ? '/ajax/like/question/' : '/ajax/like/answer/';
        const dataKey = entityType === 'question' ? 'question_id' : 'answer_id';

        sendAjaxRequest(
            url,
            {
                [dataKey]: entityId,
                value: value
            },
            function (response) {
                if (response.success) {
                    $ratingValue.text(response.new_rating);
                    
                    if (response.current_value === 1) {
                        $container.find('.like-btn').addClass('active');
                        $container.find('.dislike-btn').removeClass('active');
                    } else if (response.current_value === -1) {
                        $container.find('.like-btn').removeClass('active');
                        $container.find('.dislike-btn').addClass('active');
                    } else {
                        $container.find('.like-btn').removeClass('active');
                        $container.find('.dislike-btn').removeClass('active');
                    }
                } else {
                    $ratingValue.text(oldRating);
                    if (wasActive) {
                        $btn.addClass('active');
                    } else {
                        $btn.removeClass('active');
                    }
                    if (otherWasActive) {
                        $otherBtn.addClass('active');
                    } else {
                        $otherBtn.removeClass('active');
                    }
                    
                    if (response.error && response.error.includes('cannot like your own')) {
                        $btn.addClass('disabled-own');
                        $otherBtn.addClass('disabled-own');
                        $btn.css('opacity', '0.5');
                        $otherBtn.css('opacity', '0.5');
                        $btn.css('cursor', 'not-allowed');
                        $otherBtn.css('cursor', 'not-allowed');
                        $btn.data('own', 'true');
                        $otherBtn.data('own', 'true');
                        $btn.prop('disabled', true);
                        $otherBtn.prop('disabled', true);
                    } else if (response.error) {
                        alert('Error: ' + response.error);
                    }
                }
            },
            function (xhr) {
                $ratingValue.text(oldRating);
                if (wasActive) {
                    $btn.addClass('active');
                } else {
                    $btn.removeClass('active');
                }
                if (otherWasActive) {
                    $otherBtn.addClass('active');
                } else {
                    $otherBtn.removeClass('active');
                }
                
                if (xhr.status === 403) {
                    if (xhr.responseJSON && xhr.responseJSON.error && 
                        xhr.responseJSON.error.includes('cannot like your own')) {
                        $btn.addClass('disabled-own');
                        $otherBtn.addClass('disabled-own');
                        $btn.css('opacity', '0.5');
                        $otherBtn.css('opacity', '0.5');
                        $btn.css('cursor', 'not-allowed');
                        $otherBtn.css('cursor', 'not-allowed');
                        $btn.data('own', 'true');
                        $otherBtn.data('own', 'true');
                        $btn.prop('disabled', true);
                        $otherBtn.prop('disabled', true);
                    } else {
                        window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
                    }
                } else if (xhr.status === 400 && xhr.responseJSON && xhr.responseJSON.error) {
                    alert('Error: ' + xhr.responseJSON.error);
                } else {
                    alert('Network error. Please try again.');
                }
            }
        ).always(function() {
            activeRequest = false;
            if (!$btn.hasClass('disabled-own')) {
                $btn.prop('disabled', false);
                $otherBtn.prop('disabled', false);
                $btn.css('cursor', '');
                $otherBtn.css('cursor', '');
            }
        });

        return true;
    }

    $(document).on('click', '.question .like-btn:not(.disabled-own), .question .dislike-btn:not(.disabled-own)', function (e) {
        e.preventDefault();
        e.stopPropagation();

        const $btn = $(this);
        const $container = $btn.closest('.question');
        const questionId = $container.data('question-id');

        if (!questionId) return;

        handleLike($btn, 'question', questionId);
    });

    $(document).on('click', '.question[data-question-id] .like-btn:not(.disabled-own), .question[data-question-id] .dislike-btn:not(.disabled-own)', function (e) {
        e.preventDefault();
        e.stopPropagation();

        const $btn = $(this);
        const $container = $btn.closest('.question[data-question-id]');
        const questionId = $container.data('question-id');

        if (!questionId) return;

        handleLike($btn, 'question', questionId);
    });

    $(document).on('click', '.answer .like-btn:not(.disabled-own), .answer .dislike-btn:not(.disabled-own)', function (e) {
        e.preventDefault();
        e.stopPropagation();

        const $btn = $(this);
        const $container = $btn.closest('.answer');
        const answerId = $container.data('answer-id');

        if (!answerId) return;

        handleLike($btn, 'answer', answerId);
    });

    $(document).on('change', '.correct-checkbox input[type="checkbox"]', function () {
        if (activeRequest) {
            $(this).prop('checked', !$(this).prop('checked'));
            return;
        }

        const $checkbox = $(this);
        const $container = $checkbox.closest('.answer');
        const answerId = $container.data('answer-id');
        const isChecked = $checkbox.is(':checked');
        
        const wasChecked = !isChecked;

        if (!checkAuth()) {
            const loginUrl = '/login/?next=' + encodeURIComponent(window.location.pathname);
            window.location.href = loginUrl;
            $checkbox.prop('checked', wasChecked);
            return;
        }

        activeRequest = true;
        $checkbox.prop('disabled', true);
        $checkbox.css('cursor', 'wait');

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
                    $checkbox.prop('checked', wasChecked);
                    if (response.error) {
                        alert(response.error);
                    }
                }
            },
            function (xhr) {
                $checkbox.prop('checked', wasChecked);
                if (xhr.status === 403) {
                    alert('Only question author can mark correct answers');
                } else if (xhr.status === 400 && xhr.responseJSON && xhr.responseJSON.error) {
                    alert('Error: ' + xhr.responseJSON.error);
                } else {
                    alert('Network error. Please try again.');
                }
            }
        ).always(function() {
            activeRequest = false;
            $checkbox.prop('disabled', false);
            $checkbox.css('cursor', '');
        });
    });

    $(document).ready(function () {
        $('.like-btn.disabled-own, .dislike-btn.disabled-own').each(function() {
            $(this).attr('title', 'You cannot vote on your own content');
            $(this).css({
                'opacity': '0.5',
                'cursor': 'not-allowed'
            });
        });

        if (!checkAuth()) {
            $('.like-btn:not(.disabled-own), .dislike-btn:not(.disabled-own), .correct-checkbox input[type="checkbox"]').each(function () {
                $(this).css('cursor', 'pointer');
            });
        }

        $('.like-btn:not(.disabled-own), .dislike-btn:not(.disabled-own)').hover(
            function () {
                const $btn = $(this);
                if ($btn.hasClass('disabled-own')) {
                    $btn.attr('title', 'You cannot vote on your own content');
                    return;
                }
                
                if (!checkAuth()) {
                    $btn.attr('title', 'Login to vote');
                } else if ($btn.prop('disabled')) {
                    $btn.attr('title', 'Please wait...');
                }
            },
            function () {
                const $btn = $(this);
                if (!$btn.hasClass('disabled-own')) {
                    $btn.removeAttr('title');
                }
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
        
        if (!$('style[data-own-buttons]').length) {
            const style = document.createElement('style');
            style.setAttribute('data-own-buttons', 'true');
            style.textContent = `
                .like-btn.disabled-own, 
                .dislike-btn.disabled-own {
                    opacity: 0.5 !important;
                    cursor: not-allowed !important;
                    pointer-events: none !important;
                }
                
                .like-btn.disabled-own:hover, 
                .dislike-btn.disabled-own:hover {
                    background-color: inherit !important;
                    transform: none !important;
                    box-shadow: none !important;
                }
            `;
            document.head.appendChild(style);
        }
    });
})();