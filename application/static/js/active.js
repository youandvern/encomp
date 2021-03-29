// WINDOW.FOCUS()

function set_project_id(btnid) {
  // '<%Session["UserName"] = "' + userName + '"; %>';
  window.localStorage.setItem('current_project', btnid);
}

function highlight_project() {
  var btnid = window.localStorage.getItem('current_project')
  var select_btn = document.getElementById(btnid);
  if(select_btn) {
    var list = document.getElementsByClassName("project-bullet-selected");
    if(list[0]){
      for (var i=0, item; item = list[i]; i++) {
        item.classList.remove("project-bullet-selected");
      }
    }
    select_btn.classList.add("project-bullet-selected");
  }
}
highlight_project();


// https://www.w3schools.com/howto/howto_js_slideshow.asp
var slideIndex = 1;
var timeoutVar;
showSlides(slideIndex);

// Next/previous controls
function plusSlides(n) {
  showSlides(slideIndex += n);
}


// Thumbnail image controls
function currentSlide(n) {
  showSlides(slideIndex = n);
}

function showSlides(n) {
  clearTimeout(timeoutVar);
  var i;
  var slides = document.getElementsByClassName("index-video-slide");
  var dots = document.getElementsByClassName("dot");
  if (slides.length > 0 && dots.length > 0){
    if (n > slides.length) {slideIndex = 1}
    if (n < 1) {slideIndex = slides.length}
    for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }
    for (i = 0; i < dots.length; i++) {
        dots[i].className = dots[i].className.replace(" slide-active", "");
    }
    slides[slideIndex-1].style.display = "block";
    dots[slideIndex-1].className += " slide-active";
    timeoutVar = setTimeout(function() { plusSlides(1); }, 6000); // Change image every 6 seconds
  }

}


function projCalcDisplay(){
  //show calcs associated with given projects
}

function deletedProject(){
  window.localStorage.removeItem('current_project')
}

function openProjectForm() {
  document.getElementById("addProjectForm").style.display = "block";
}

function closeProjectForm() {
  document.getElementById("addProjectForm").style.display = "none";
}

function openProjectChangeForm(clicked_ID) {
  var btnid = window.localStorage.getItem('current_project')

  if(btnid) {
    if(btnid == clicked_ID){
      event.preventDefault();
      document.getElementById("changeProjectNameForm").style.display = "block";
      return false;
    }
  }
}

function closeProjectChangeForm() {
  document.getElementById("changeProjectNameForm").style.display = "none";
}

function openCalcForm() {
  document.getElementById("addCalcForm").style.display = "block";
  // formatSelector()
}

function closeCalcForm() {
  document.getElementById("addCalcForm").style.display = "none";
}

function openCalcChangeForm() {
  document.getElementById("changeCalcNameForm").style.display = "block";
}

function closeCalcChangeForm() {
  document.getElementById("changeCalcNameForm").style.display = "none";
}

function openDeleteCalcForm() {
  document.getElementById("deleteCalcForm").style.display = "block";
}

function closeDeleteCalcForm() {
  document.getElementById("deleteCalcForm").style.display = "none";
}

function clearProjectStorage(){
  window.localStorage.setItem('current_project', "");
}

if (document.getElementById("addProjectForm")){
  dragElement(document.getElementById("addProjectForm"));
}
if (document.getElementById("addCalcForm")){
  dragElement(document.getElementById("addCalcForm"));
}
if (document.getElementById("changeProjectNameForm")){
  dragElement(document.getElementById("changeProjectNameForm"));
}
if (document.getElementById("changeCalcNameForm")){
  dragElement(document.getElementById("changeCalcNameForm"));
}
if (document.getElementById("deleteCalcForm")){
  dragElement(document.getElementById("deleteCalcForm"));
}



// Make the DIV element draggable: https://www.w3schools.com/howto/howto_js_draggable.asp
function dragElement(elmnt) {
  var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
  if (document.getElementById(elmnt.id + "Header")) {
    // if present, the header is where you move the DIV from:
    document.getElementById(elmnt.id + "Header").onmousedown = dragMouseDown;
  } else {
    // otherwise, move the DIV from anywhere inside the DIV:
    var moveables = elmnt.querySelectorAll(':not(select):not(form):not(fieldset):not(div):not(input):not(button):not(textarea)');
    var numelmnt = moveables.length;
    for (var i = 0; i < numelmnt; i++) {
      moveables[i].style.cursor = "grab";
      moveables[i].onmousedown = dragMouseDown;
      //Do something
    }
    // elmnt.onmousedown = dragMouseDown;
  }

  function dragMouseDown(e) {
    e = e || window.event;
    e.preventDefault();
    // get the mouse cursor position at startup:
    pos3 = e.clientX;
    pos4 = e.clientY;
    document.onmouseup = closeDragElement;
    // call a function whenever the cursor moves:
    document.onmousemove = elementDrag;
  }

  function elementDrag(e) {
    e = e || window.event;
    e.preventDefault();
    // calculate the new cursor position:
    pos1 = pos3 - e.clientX;
    pos2 = pos4 - e.clientY;
    pos3 = e.clientX;
    pos4 = e.clientY;
    // set the element's new position:
    elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
    elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
  }

  function closeDragElement() {
    // stop moving when mouse button is released:

    document.onmouseup = null;
    document.onmousemove = null;
  }
}





// -------------formatting select form entries with bootstrap -------------------------
function set_custom_select_class(){
  var select_div = document.getElementsByClassName('select-type');
  var indx1;
  var lenselect = select_div.length;
  for (indx1 = 0; indx1 < lenselect; indx1++) {
    selElmnt = select_div[indx1].getElementsByTagName('select')[0];
    selElmnt.className = "custom-select";
  }
}
set_custom_select_class();
