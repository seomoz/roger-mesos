$env_name = 'unknown'; // this should be replaced with actual environment name during installation
$actas_cookie_name = "aaadactas"; // this should be replaced if the cookie name is different
$aaadselectorClicked = false;
$(document).ready(function(){
  $('head').append('<link rel="stylesheet" type="text/css" href="/static/aaad-ui.css">');
  var $elm = '<div id="aaadcontainer"><div id="aaaddropdown">Welcome to RogerOS! This is the <b>' + $env_name + '</b> environment.' + getActAsDetails() +
             '</div><div id="aaadselector"><table><tbody><tr><td><img class="rogermascotimg" src="/static/roger-blue.png"/></td><td>-: ' + $env_name + ' :-</td><td><img class="rogermascotimg" src="/static/roger-blue.png"/></td></tr></tbody></table></div></div>'
  $('body').append($elm)
  $(aaadselector).click(function () {
    $aaadselectorClicked = true;
    $(aaaddropdown).slideToggle(300);
  });

  if (getCookieValue($actas_cookie_name)) {
    // If the user is (or was) already logged in let's check in a few seconds...
    setTimeout(function(){
      // ... and if dropdown is still visible, let's slideToggle to hide it
      if(!$aaadselectorClicked && $('#aaaddropdown').css('display') != 'none') {
        $(aaaddropdown).slideToggle(300);
      }
    }, 5000);
  }
});
function getActAsDetails() {
  // Returns a line (string) based on whether the actas cookie is available
  var $actas = getCookieValue($actas_cookie_name);
  if ($actas) {
    return ' You\'re acting as <b>' + $actas + '</b> <a href="#" onclick="onActAsChangeClick();return false;">[change]</a> | <a href="/logout">[log out].</a>';
  }
  return ' Please <a href="/login">[log in]</a>.';
}
function getCookieValue(a) {
  b = document.cookie.match('(^|;)\\s*' + a + '\\s*=\\s*([^;]+)');
  return b ? b.pop() : '';
}
function onActAsChangeClick() {
  window.location.href = '/login?resetactas=true&next=' + encodeURIComponent(window.location.href);
}
