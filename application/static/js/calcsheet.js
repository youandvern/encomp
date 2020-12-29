// window.MathJax = {
//   startup: {
//     ready: () => {
//       MathJax.startup.defaultReady();
//       MathJax.startup.promise.then(() => {
//         // var pagedscript = document.createElement('script');
//         // pagedscript.setAttribute('src','https://unpkg.com/pagedjs/dist/paged.polyfill.js');
//         // document.head.appendChild(pagedscript);
//         // console.log('MathJax initial typesetting complete');
//         // window.location.href = window.location.href;
//       });
//     }
//   }
// };

function postLoadedScript() {
  var pagedscript = document.createElement('script');
  pagedscript.setAttribute('src','https://unpkg.com/pagedjs/dist/paged.polyfill.js');
  document.head.appendChild(pagedscript);
  // console.log('MathJax initial typesetting complete');
}

document.addEventListener("load", postLoadedScript());
