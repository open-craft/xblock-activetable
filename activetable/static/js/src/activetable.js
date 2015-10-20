/* Javascript for ActiveTableXBlock. */
function ActiveTableXBlock(runtime, element, init_args) {

    var checkHandlerUrl = runtime.handlerUrl(element, 'check_answers');

    function updateStatus(num_total, num_correct) {
        var $status = $('.status', element);
        var $status_message = $('.status-message', element);
        if (num_total == num_correct) {
            $status.removeClass('incorrect').addClass('correct');
            $status_message.text('Great job!');
        } else {
            $status.removeClass('correct').addClass('incorrect');
            $status_message.text(
                'You have ' + num_correct + ' out of ' + num_total + ' cells correct.'
            );
        }
    }

    function markResponseCells(correct_dict) {
        var num_total = 0, num_correct = 0;
        $.each(correct_dict, function(cell_id, correct) {
            var $cell = $('#' + cell_id, element);
            $cell.removeClass('right-answer wrong-answer unchecked');
            if (correct) $cell.addClass('right-answer')
            else $cell.addClass('wrong-answer');
            num_total += 1;
            num_correct += correct;
        });
        updateStatus(num_total, num_correct);
    }

    function checkAnswers(e) {
        answers = {};
        $('td.active', element).each(function() {
            answers[this.id] = $('input', this).val();
        });
        $.ajax({
            type: "POST",
            url: checkHandlerUrl,
            data: JSON.stringify(answers),
            success: markResponseCells,
        });
    }

    function toggleHelp(e) {
        var $help_text = $('#activetable-help-text', element);
        $help_text.toggle();
        $(this).text($help_text.is(':visible') ? '-help' : '+help');
    }

    $('#activetable-help-button', element).click(toggleHelp);
    $('.action .check', element).click(checkAnswers);
    if (init_args.num_total_answers) {
        updateStatus(init_args.num_total_answers, init_args.num_correct_answers);
    }
}
