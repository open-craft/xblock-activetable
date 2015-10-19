/* Javascript for ActiveTableXBlock. */
function ActiveTableXBlock(runtime, element) {

    var checkHandlerUrl = runtime.handlerUrl(element, 'check_answers');

    function markResponseCells(correct_dict) {
        $.each(correct_dict, function(cell_id, correct) {
            var $cell = $('#' + cell_id, element);
            $cell.removeClass('right-answer wrong-answer unchecked');
            if (correct) $cell.addClass('right-answer')
            else $cell.addClass('wrong-answer');
        })
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
}
