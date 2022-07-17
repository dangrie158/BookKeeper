(function () {
    'use strict'

    document.querySelector('#navbarSideCollapse').addEventListener('click', function () {
        document.querySelector('.offcanvas-collapse').classList.toggle('open')
        console.log(document.querySelector('.offcanvas-collapse'))
    })
})()
