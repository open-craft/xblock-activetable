/* Javascript for ActiveTableXBlock. */
function ActiveTableXBlock(runtime, element, init_args) {

    var checkHandlerUrl = runtime.handlerUrl(element, 'check_answers');
    var saveHandlerUrl = runtime.handlerUrl(element, 'save_answers');

    function markResponseCells(data) {
        if (data.answers_correct) {
            $.each(data.answers_correct, function(cell_id, correct) {
                var $cell = $('#' + cell_id, element);
                $cell.removeClass('right-answer wrong-answer unchecked');
                if (correct) {
                    $cell.addClass('right-answer');
                    $cell.prop('title', 'correct');
                } else {
                    $cell.addClass('wrong-answer');
                    $cell.prop('title', 'incorrect');
                }
            });
        } else {
            $('td.active', element).removeClass('right-answer wrong-answer').addClass('unchecked');
        }
    }

    function updateStatusMessage(data) {
        var $status = $('.status', element);
        var $status_message = $('.status-message', element);
        if (!data.answers_correct) {
            $status.removeClass('incorrect correct');
            $status.text('unanswered');
            $status_message.text('');
        }
        else if (data.num_total_answers == data.num_correct_answers) {
            $status.removeClass('incorrect').addClass('correct');
            $status.text('correct');
            $status_message.text('Great job!');
        } else {
            $status.removeClass('correct').addClass('incorrect');
            $status.text('incorrect');
            $status_message.text(
                'You have ' + data.num_correct_answers + ' out of ' + data.num_total_answers +
                ' cells correct.'
            );
        }
    }

    function updateFeedback(data) {
        var feedback_msg;
        if (data.score === null) {
            feedback_msg = '(' + data.max_score + ' points possible)';
        } else {
            feedback_msg = '(' + data.score + '/' + data.max_score + ' points)';
        }
        if (data.max_attempts) {
            feedback_msg = 'You have used ' + data.attempts + ' of ' + data.max_attempts +
                ' submissions ' + feedback_msg;
            if (data.attempts == data.max_attempts - 1) {
                $('.action .check .check-label', element).text('Final check');
            }
            else if (data.attempts >= data.max_attempts) {
                $('.action .check, .action .save', element).hide();
            }
        }
        $('.submission-feedback', element).text(feedback_msg);
    }

    function updateStatus(data) {
        markResponseCells(data);
        updateStatusMessage(data);
        updateFeedback(data);
    }

    function callHandler(url) {
        var answers = {};
        $('td.active', element).each(function() {
            answers[this.id] = $('input', this).val();
        });
        $.ajax({
            type: "POST",
            url: url,
            data: JSON.stringify(answers),
            success: updateStatus,
        });
    }

    function toggleHelp(e) {
        var $help_text = $('#activetable-help-text', element);
        $help_text.toggle();
        $(this).text($help_text.is(':visible') ? '-help' : '+help');
    }

    $('#activetable-help-button', element).click(toggleHelp);
    $('.action .check', element).click(function (e) { callHandler(checkHandlerUrl); });
    $('.action .save', element).click(function (e) { callHandler(saveHandlerUrl); });
    updateStatus(init_args);
}
