
document.addEventListener("DOMContentLoaded", function() {

	const portfolioContainer = document.getElementById('portfolioContainer')
	const portfolioTabs = portfolioContainer.querySelectorAll('.portfolio-tab')
	const serviceItems = document.querySelectorAll('.service-item')
	var bannerLinks = document.querySelectorAll('.carousel-item');

	function serviceToggle(element){
		for (let i=0;i<serviceItems.length;i++) {
			serviceItems[i].classList.remove('active')
			portfolioTabs[i].classList.remove('active')
		}
		const parentNode = element.parentElement
		const index = Array.from(parentNode.children).indexOf(element)
		serviceItems[index].classList.add('active')
		portfolioTabs[index].classList.add('active')

		portfolioContainer.classList.remove('hidden')
		portfolioContainer.scrollIntoView({behavior: "smooth"})
	}

	bannerLinks.forEach( (item) => {
		item.addEventListener('click', (el) => {
			serviceToggle(el.currentTarget)
		}, {passive: true})
	})

	serviceItems.forEach( (item) => {
		item.addEventListener('click', (el) => {
			serviceToggle(el.currentTarget)
		}, {passive: true})
	})


	const modalContainer = document.getElementById('modalContainer')
	const sliderContainer = modalContainer.querySelector('.carousel-inner')
	const sliderControls = modalContainer.querySelector('.controls-block')

	//var modal = new bootstrap.Modal(modalContainer)
	modalContainer.addEventListener('show.bs.modal', function (event) {
		if (!sliderContainer) return event.preventDefault()
		const target = event.relatedTarget

		var sourceImageWrapper = document.querySelectorAll(`#portfolio-${target.dataset.parent} a`)
		var list = Array.prototype.slice.call(sourceImageWrapper)
		list.forEach(function(el) {
			var node = document.createElement('div')
			node.classList = 'carousel-item'
			if (list.indexOf(el) == Number(target.dataset.index)) {
				node.classList.add('active')
			}
			let img = el.querySelector('img')
			img.classList = 'centered'
			img.setAttribute('loading', 'auto')
			node.appendChild(img.cloneNode(true))
			let title = target.dataset.title
			let descr = target.dataset.description
			if (title || descr) {
				let meta = `<div class="caption"><h5>${title}</h5><p>${descr}</p></div>`
				node.insertAdjacentHTML('beforeend', meta)
			}
			sliderContainer.append(node)
		})
		// скроем стрелки, если фото одна в слайдере
		sliderControls.style.display = (list.length == 1) ? 'none': 'block'
	})

	modalContainer.addEventListener('hidden.bs.modal', function (event) {
		while (sliderContainer.firstChild) {
			sliderContainer.removeChild(sliderContainer.lastChild)
		}
	})

	var scrollUp = document.querySelector('#back2top');
	document.onscroll = function(e) {
		if (scrollUp) {
			if (window.pageYOffset <= window.innerHeight) {
				if (! scrollUp.classList.contains('disable')) {
					scrollUp.classList.add('disable');
					scrollUp.style.transform = `translateY(${scrollUp.parentElement.clientHeight*2}px)`;
				}
			} else
				if (scrollUp.classList.contains('disable')) {
					scrollUp.classList.remove('disable');
					scrollUp.style.transform = `translateY(${-scrollUp.parentElement.clientHeight}px)`;
				}
		}
	}


	scrollUp && scrollUp.addEventListener('click', function (e) {
		e.preventDefault()
		serviceItems[0].scrollIntoView({behavior: "smooth"})

	})

})
