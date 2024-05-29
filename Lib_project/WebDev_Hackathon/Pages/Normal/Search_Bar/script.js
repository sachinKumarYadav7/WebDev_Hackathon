document.addEventListener('DOMContentLoaded', () => {
    const searchBar = document.querySelector('.search-bar');
    const buttonsContainer = document.querySelector('.buttons-container');
    const filterButton = document.querySelector('.filter-button');
    const filterModal = document.getElementById('filterModal');
    const closeModal = document.getElementsByClassName('close')[0];
  
    searchBar.addEventListener('focus', () => {
      buttonsContainer.style.display = 'flex';
      document.querySelector('.search-container').style.transform = 'translateY(-50%)';
    });
  
    searchBar.addEventListener('blur', () => {
      setTimeout(() => {
        buttonsContainer.style.display = 'none';
        document.querySelector('.search-container').style.transform = 'translateY(0)';
      }, 200); // Delay to allow click event on suggestions
    });
  
    filterButton.addEventListener('click', () => {
      filterModal.style.display = 'block';
    });
  
    closeModal.onclick = function() {
      filterModal.style.display = 'none';
    }
  
    window.onclick = function(event) {
      if (event.target == filterModal) {
        filterModal.style.display = 'none';
      }
    }
  });
  
  function applyFilters() {
    const author = document.getElementById('author').value;
    const genre = document.getElementById('genre').value;
    const year = document.getElementById('year').value;
    const rating = document.getElementById('rating').value;
  
    // Logic to filter books from database based on the filters
    // For now, we'll just log the filters to the console
    console.log(`Filtering books by:
      Author: ${author},
      Genre: ${genre},
      Published Year: ${year},
      Rating: ${rating}`);
    
    // Close the modal after applying filters
    document.getElementById('filterModal').style.display = 'none';
  }
  