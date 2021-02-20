var print_button_section = document.getElementById("print_button_section");
if (print_button_section) {
  console.log("found button");
} else {
  console.log("button not foung");
}


function page_format_and_print() {

  function myprintfunction(module) {
    setTimeout(() => {
  		window.PagedPolyfill.preview().then(module => window.print());
  	}, 1000);
  }

  let pagedscript = import('/static/js/paged.polyfill.js?v=1').then(module => myprintfunction(module)); // .then(module => myprintfunction(module)); // .then(window.print());
  // console.log(pagedscript);
  window.PagedConfig = {
		auto: false // ,
		// after: (flow) => { console.log("after", flow) },
	};


}

function hide_print_button() {
  if (print_button_section) {
    console.log("button hidden");
    print_button_section.style.display = "none";
  } else {
    console.log("button not found")
  }

}

function auto_print_report(){
  hide_print_button();

  document.addEventListener("load",MathJax.Hub.Queue( () => page_format_and_print()));
}

function click_print_report(){
  hide_print_button();
  page_format_and_print();
}

// document.addEventListener("load", postLoadedScript());
