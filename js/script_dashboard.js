document.addEventListener('DOMContentLoaded', () => {
  // Card stack logic
  const cards = document.querySelectorAll('.card');
  let currentIndex = 0;

  function showNextCard() {
    cards.forEach((card, index) => {
      if (index === currentIndex) {
        card.style.transform = `translateZ(${index * -20}px)`;
        card.style.opacity = 1;
      } else {
        card.style.transform = `translateZ(${(index - currentIndex) * -20}px)`;
        card.style.opacity = 0;
      }
    });

    currentIndex = (currentIndex + 1) % cards.length;
  }

  // Show next card every 3 seconds
  setInterval(showNextCard, 3000);

  // Initial setup
  showNextCard();

  // Advertisement logic
  const advertisements = document.querySelectorAll('.advertisement');
  let currentAdIndex = 0;

  function showNextAdvertisement() {
    advertisements.forEach((ad, index) => {
      if (index === currentAdIndex) {
        ad.classList.add('active');
      } else {
        ad.classList.remove('active');
      }
    });

    currentAdIndex = (currentAdIndex + 1) % advertisements.length;
  }

  // Show next advertisement every 5 seconds
  setInterval(showNextAdvertisement, 5000);

  // Initial setup
  showNextAdvertisement();
});
