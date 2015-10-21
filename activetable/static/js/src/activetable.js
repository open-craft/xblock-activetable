/* Javascript for ActiveTableXBlock. */
function ActiveTableXBlock(runtime, element, init_args) {

    var checkHandlerUrl = runtime.handlerUrl(element, 'check_answers');

    function updateStatus(data) {
        var $status = $('.status', element);
        var $status_message = $('.status-message', element);
        if (data.num_total_answers == data.num_correct_answers) {
            $status.removeClass('incorrect').addClass('correct');
            $status.text('correct');
            $status_message.text('Great job! (' + data.score + '/' + data.max_score + ' points)');
        } else {
            $status.removeClass('correct').addClass('incorrect');
            $status.text('incorrect');
            $status_message.text(
                'You have ' + data.num_correct_answers + ' out of ' + data.num_total_answers +
                ' cells correct. (' + data.score + '/' + data.max_score + ' points)'
            );
        }
    }

    function markResponseCells(data) {
        $.each(data.correct, function(cell_id, correct) {
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
        updateStatus(data);
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
    if (init_args.num_total_answers) updateStatus(init_args);
}
