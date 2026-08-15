const revealItems = document.querySelectorAll('.reveal');

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('show');
      }
    });
  },
  { threshold: 0.2 }
);

revealItems.forEach((item, index) => {
  item.style.transitionDelay = `${index * 0.06}s`;
  observer.observe(item);
});

const counters = document.querySelectorAll('.counter');

const animateCounter = (counter) => {
  const target = Number(counter.dataset.target);
  const duration = 1200;
  const start = performance.now();
  const hasDecimal = String(target).includes('.');

  const step = (time) => {
    const progress = Math.min((time - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = target * eased;

    counter.textContent = hasDecimal ? current.toFixed(1) : Math.floor(current).toString();

    if (progress < 1) {
      requestAnimationFrame(step);
    }
  };

  requestAnimationFrame(step);
};

const counterObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting && !entry.target.dataset.done) {
        entry.target.dataset.done = 'true';
        animateCounter(entry.target);
      }
    });
  },
  { threshold: 0.8 }
);

counters.forEach((counter) => counterObserver.observe(counter));
