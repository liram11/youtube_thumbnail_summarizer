

// import {
//   computePosition,
//   flip,
//   shift,
//   offset,
//   ReferenceElement,
// } from '@floating-ui/dom';



//eslint-disable-next-line
function hasClass(elem: any, className: string) {
  return elem?.classList.contains(className);
}


function addTooptip(parent: ParentNode | HTMLElement | null) {
  if (!parent?.querySelector('.clickbait-checker-tooltip')) {
    const tooltip = document.createElement('div')

    tooltip.classList.add('clickbait-checker-tooltip')
    tooltip.innerHTML = 'This is a tooltip'
    parent?.appendChild(tooltip)
  }

}

document.addEventListener('mouseover', (e) => {
  if (e.target && hasClass(e.target, 'yt-core-image--loaded')) {
    const target = e.target as HTMLElement

    console.log('parent', target.parentNode)

    addTooptip(target.parentNode)


    const videoPreviewContainer = document.getElementById('video-preview-container')

    addTooptip(videoPreviewContainer)

    // computePosition(target, tooltip, {
    //   placement: 'top',
    //   middleware: [offset(6), flip(), shift({padding: 5})],
    // }).then(({x, y}) => {
    //   Object.assign(tooltip.style, {
    //     left: `${x}px`,
    //     top: `${y}px`,
    //   });
    // });
    console.log('tooltip added')

  }
}, false);


// const button = document.querySelector('#button');
