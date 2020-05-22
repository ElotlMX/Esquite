$(document).ready(function () {
  $('[data-toggle="tooltip"]').tooltip();

  function keyboard_display_control(){
    let languageSelector = $('#id_idioma');
      if(languageSelector.val() === "L2") {
        $('#keyboard-container').collapse('show');
      }
      languageSelector.change(() => {
        if(languageSelector.val() === "L2"){
          $('#keyboard-container').collapse('show');
        }else{
          $('#keyboard-container').collapse('hide');
        }
      });
  }


  function keyboard_handler() {
      let keyboardButton = $('.btn-keyboard');
      keyboardButton.click((event) => {
        let queryField = $('input#id_busqueda');
        let currentQuery = queryField.val();
        queryField.val(currentQuery + event.target.value);
      });
  }

  // Function Calls
  keyboard_display_control();
  keyboard_handler();
});
