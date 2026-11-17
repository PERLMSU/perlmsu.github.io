document.addEventListener('DOMContentLoaded', function () {
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.site-nav');

  if (!toggle || !nav) return;

  const submenus = nav.querySelectorAll('.has-submenu');

  function closeSubmenus(except) {
    submenus.forEach(function (item) {
      if (item === except) return;
      item.classList.remove('is-open');
      item.querySelector('.submenu-toggle').setAttribute('aria-expanded', 'false');
    });
  }

  submenus.forEach(function (item) {
    const button = item.querySelector('.submenu-toggle');
    button.addEventListener('click', function () {
      const isOpen = item.classList.toggle('is-open');
      button.setAttribute('aria-expanded', isOpen);
      closeSubmenus(item);
    });
  });

  toggle.addEventListener('click', function () {
    const isOpen = nav.classList.toggle('is-open');
    toggle.setAttribute('aria-expanded', isOpen);
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeSubmenus();
    if (e.key === 'Escape' && nav.classList.contains('is-open')) {
      nav.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.focus();
    }
  });

  document.addEventListener('click', function (e) {
    if (!nav.contains(e.target) && !toggle.contains(e.target)) {
      closeSubmenus();
      nav.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
    }
  });
});
