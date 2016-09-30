$env_name = 'unknown'; // this should be replaced with actual environment name during installation
$actas_cookie_name = "aaadactas"; // this should be replaced if the cookie name is different
$aaadselectorClicked = false;
$username = ''
$aaad_update_timer_id = 0
$(document).ready(function(){
  $('head').append('<link rel="stylesheet" type="text/css" href="/static/aaad-ui.css">');
  var $elm = '<div id="aaadcontainer"><div id="aaaddropdown"><table width="100%"><tr><td width="33%"align="left"></td><td width="34%" align="center">Welcome to RogerOS! This is the <b>' + $env_name + '</b> environment.</td><td width="33%" align="right"><div id="welcomeuser">Hello! Please <a href="/login">[log in]</a></div><div id="actasdetails"/></td></tr></table>' +
             '</div><div id="aaadselector"><table><tbody><tr><td><img class="rogermascotimg" src="/static/roger-blue.png"/></td><td>-: ' + $env_name + ' :-</td><td><img class="rogermascotimg" src="/static/roger-blue.png"/></td></tr></tbody></table></div></div>'
  $('body').append($elm)
  updateUserDetails()
  $(aaadselector).click(function () {
    $aaadselectorClicked = true;
    $(aaaddropdown).slideToggle(300);
    if($('#aaaddropdown').css('display') != 'none') {
      updateUserDetails()
      $aaad_update_timer_id = setInterval(updateUserDetails, 10000);
    } else {
      if ($aaad_update_timer_id != 0) {
        clearInterval($aaad_update_timer_id);
      }
    }
  });
  if (getCookieValue($actas_cookie_name)) {
    // If the user is (or was) already logged in let's check in a few seconds...
    setTimeout(function(){
      // ... and if dropdown is still visible, let's slideToggle to hide it
      if(!$aaadselectorClicked && $('#aaaddropdown').css('display') != 'none') {
        $(aaaddropdown).slideToggle(300);
        if ($aaad_update_timer_id != 0) {
          clearInterval($aaad_update_timer_id);
        }
      }
    }, 5000);
  }
});
function updateUserDetails() {
  $.getJSON( "/login/user" )
    .done(function (responseData) {
      $username = responseData["username"];
      if(isEmpty($username)) {
        $('#welcomeuser').html('Hello! Please <a href="/login">[log in]</a>');
        $('#actasdetails').html('');
      } else {
        $('#welcomeuser').html('Hello <b>' + $username + '</b>!');
        var $actas = getCookieValue($actas_cookie_name);
        if (isEmpty($actas) || $actas == $username) {
          $actas = 'yourself';
        }
        $('#actasdetails').html(' You\'re acting as <b>' + $actas + '</b> <a href="#" onclick="onActAsChangeClick();return false;">[change]</a> | <a href="/logout">[log out]</a>');
      }
    });
}
function getCookieValue(a) {
  b = document.cookie.match('(^|;)\\s*' + a + '\\s*=\\s*([^;]+)');
  return b ? b.pop() : '';
}
function onActAsChangeClick() {
  window.location.href = '/login?resetactas=true&next=' + encodeURIComponent(window.location.href);
}
function isEmpty(str) {
    return (!str || 0 === str.length);
}
