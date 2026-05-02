/**
 * Search, Filter, and Sort functionality for products
 * Works with the header search bar and filters dropdown
 */

class ProductSearchFilter {
    constructor() {
        // Product data will be populated from the HTML
        this.allProducts = [];
        this.filteredProducts = [];
        this.currentSort = 'relevant';
        this.activeFilters = {
            priceRanges: [],
            discounts: [],
            ratings: [],
            availability: []
        };
        this.searchTerm = '';

        this.initializeProducts();
        this.setupEventListeners();
    }

    /**
     * Extract product data from the DOM
     */
    initializeProducts() {
        const offerCards = document.querySelectorAll('.offer-card');
        const products = [];

        offerCards.forEach((card, index) => {
            const name = card.querySelector('.offer-name')?.textContent.trim() || '';
            const oldPrice = parseFloat(
                card.querySelector('.offer-old-price')?.textContent.replace('£', '') || 0
            );
            const currentPrice = parseFloat(
                card.querySelector('.offer-current-price')?.textContent.replace('£', '') || 0
            );
            const discountPercent = parseInt(
                card.querySelector('.offer-badge')?.textContent.replace('-', '').replace('%', '') || 0
            );
            const ratingStars = card.querySelectorAll('.card-seller-rating')[0]?.textContent.match(/★/g)?.length || 0;

            // Generate a simple product ID if not available
            const productId = index + 1;

            products.push({
                id: productId,
                name: name,
                oldPrice: oldPrice,
                currentPrice: currentPrice,
                discountPercent: discountPercent,
                rating: ratingStars,
                availability: 'in-stock', // Default - could be enhanced
                element: card,
                visible: true
            });
        });

        this.allProducts = products;
        this.filteredProducts = [...this.allProducts];
    }    /**
     * Setup event listeners for header search and filters
     */
    setupEventListeners() {
        // Search input
        const headerSearchInput = document.getElementById('headerSearch');
        if (headerSearchInput) {
            headerSearchInput.addEventListener('input', (e) => {
                this.searchTerm = e.target.value.toLowerCase().trim();
                this.showLiveSearchDropdown(this.searchTerm);
                this.applyFiltersAndSearch();
            });
            
            // Close dropdown when losing focus
            headerSearchInput.addEventListener('blur', () => {
                setTimeout(() => {
                    this.hideLiveSearchDropdown();
                }, 200);
            });

            // Show dropdown when focusing if there's a search term
            headerSearchInput.addEventListener('focus', () => {
                if (this.searchTerm.length > 0) {
                    this.showLiveSearchDropdown(this.searchTerm);
                }
            });
        }

        // Clear button
        const headerClearBtn = document.getElementById('headerClearBtn');
        if (headerClearBtn) {
            headerClearBtn.addEventListener('click', () => {
                if (headerSearchInput) {
                    headerSearchInput.value = '';
                }
                this.searchTerm = '';
                this.applyFiltersAndSearch();
            });
        }

        // Price filters
        document.querySelectorAll('.header-filter-option input[id^="header-price-"]').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                this.updateFilter('priceRanges', e.target.value, e.target.checked);
                this.applyFiltersAndSearch();
            });
        });

        // Discount filters
        document.querySelectorAll('.header-filter-option input[id^="header-discount-"]').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                this.updateFilter('discounts', e.target.value, e.target.checked);
                this.applyFiltersAndSearch();
            });
        });

        // Rating filters
        document.querySelectorAll('.header-filter-option input[id^="header-rating-"]').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                this.updateFilter('ratings', e.target.value, e.target.checked);
                this.applyFiltersAndSearch();
            });
        });

        // Availability filters
        document.querySelectorAll('.header-filter-option input[id^="header-availability-"]').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                this.updateFilter('availability', e.target.value, e.target.checked);
                this.applyFiltersAndSearch();
            });
        });

        // Sort buttons
        document.querySelectorAll('.header-sort-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                // Update active state
                document.querySelectorAll('.header-sort-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                this.currentSort = btn.dataset.sort;
                this.applyFiltersAndSearch();
                console.log('Applied sort:', this.currentSort);
            });
        });
    }

    /**
     * Update filter state
     */
    updateFilter(filterType, value, isChecked) {
        const filterArray = this.activeFilters[filterType];

        if (isChecked && !filterArray.includes(value)) {
            filterArray.push(value);
        } else if (!isChecked) {
            const index = filterArray.indexOf(value);
            if (index > -1) {
                filterArray.splice(index, 1);
            }
        }
    }

    /**
     * Apply all filters and search, then sort results
     */
    applyFiltersAndSearch() {
        let filtered = [...this.allProducts];

        // Apply search filter
        if (this.searchTerm) {
            filtered = filtered.filter(product =>
                product.name.toLowerCase().includes(this.searchTerm)
            );
        }

        // Apply price range filter
        if (this.activeFilters.priceRanges.length > 0) {
            filtered = filtered.filter(product => {
                return this.activeFilters.priceRanges.some(range => {
                    switch (range) {
                        case '0-50':
                            return product.currentPrice >= 0 && product.currentPrice <= 50;
                        case '50-100':
                            return product.currentPrice > 50 && product.currentPrice <= 100;
                        case '100-200':
                            return product.currentPrice > 100 && product.currentPrice <= 200;
                        case '200+':
                            return product.currentPrice > 200;
                        default:
                            return true;
                    }
                });
            });
        }

        // Apply discount filter
        if (this.activeFilters.discounts.length > 0) {
            filtered = filtered.filter(product => {
                return this.activeFilters.discounts.some(discountLevel => {
                    switch (discountLevel) {
                        case '10+':
                            return product.discountPercent >= 10;
                        case '25+':
                            return product.discountPercent >= 25;
                        case '50+':
                            return product.discountPercent >= 50;
                        default:
                            return true;
                    }
                });
            });
        }

        // Apply rating filter
        if (this.activeFilters.ratings.length > 0) {
            filtered = filtered.filter(product => {
                return this.activeFilters.ratings.some(ratingLevel => {
                    switch (ratingLevel) {
                        case '5':
                            return product.rating === 5;
                        case '4+':
                            return product.rating >= 4;
                        case '3+':
                            return product.rating >= 3;
                        default:
                            return true;
                    }
                });
            });
        }

        // Apply availability filter (currently all are in-stock by default)
        if (this.activeFilters.availability.length > 0) {
            filtered = filtered.filter(product => {
                return this.activeFilters.availability.includes(product.availability);
            });
        }

        // Apply sorting
        filtered = this.applySorting(filtered);

        // Update visibility
        this.updateProductVisibility(filtered);
        this.filteredProducts = filtered;

        // Log results
        console.log('Search term:', this.searchTerm);
        console.log('Active filters:', this.activeFilters);
        console.log('Sorted by:', this.currentSort);
        console.log('Showing', filtered.length, 'of', this.allProducts.length, 'products');
    }

    /**
     * Apply sorting to filtered products
     */
    applySorting(products) {
        const sorted = [...products];

        switch (this.currentSort) {
            case 'price-low':
                sorted.sort((a, b) => a.currentPrice - b.currentPrice);
                break;
            case 'price-high':
                sorted.sort((a, b) => b.currentPrice - a.currentPrice);
                break;
            case 'newest':
                // Reverse order (assuming newer items were added later)
                sorted.reverse();
                break;
            case 'popular':
                // Could be based on sales count, but for now keeping original order
                // In a real app, this would use a popularity metric
                break;
            case 'rating':
                sorted.sort((a, b) => b.rating - a.rating);
                break;
            case 'discount':
                sorted.sort((a, b) => b.discountPercent - a.discountPercent);
                break;
            case 'relevant':
            default:
                // Keep original order (most relevant is the default)
                break;
        }

        return sorted;
    }

    /**
     * Update product visibility in the DOM
     */
    updateProductVisibility(visibleProducts) {
        // Hide all products
        this.allProducts.forEach(product => {
            product.element.style.display = 'none';
            product.visible = false;
        });

        // Show filtered products in sorted order
        visibleProducts.forEach(product => {
            product.element.style.display = 'block';
            product.visible = true;
        });

        // Show "no results" message if needed
        this.updateNoResultsMessage(visibleProducts.length === 0);
    }

    /**
     * Show or hide "no results" message
     */
    updateNoResultsMessage(shouldShow) {
        let noResultsMsg = document.getElementById('no-results-message');

        if (shouldShow) {
            if (!noResultsMsg) {
                const offersSection = document.querySelector('.offers-section');
                if (offersSection) {
                    noResultsMsg = document.createElement('div');
                    noResultsMsg.id = 'no-results-message';
                    noResultsMsg.style.cssText = `
                        text-align: center;
                        padding: 2rem;
                        color: #999;
                        font-size: 1.1rem;
                        margin: 2rem 0;
                    `;
                    noResultsMsg.textContent = 'No products found matching your filters and search criteria.';
                    offersSection.appendChild(noResultsMsg);
                }
            }
        } else {
            if (noResultsMsg) {
                noResultsMsg.remove();
            }
        }    }

    /**
     * Show live search dropdown with matching products
     */
    showLiveSearchDropdown(searchTerm) {
        if (!searchTerm || searchTerm.length === 0) {
            this.hideLiveSearchDropdown();
            return;
        }

        // Find matching products
        const matches = this.allProducts.filter(product =>
            product.name.toLowerCase().includes(searchTerm)
        );

        if (matches.length === 0) {
            this.hideLiveSearchDropdown();
            return;
        }

        // Create or get dropdown container
        let dropdown = document.getElementById('live-search-dropdown');
        if (!dropdown) {
            dropdown = document.createElement('div');
            dropdown.id = 'live-search-dropdown';
            dropdown.className = 'live-search-dropdown';
            
            const headerSearchWrapper = document.querySelector('.header-search-wrapper');
            if (headerSearchWrapper) {
                headerSearchWrapper.appendChild(dropdown);
            }
        }

        // Build dropdown HTML
        let html = '<div class="live-search-results">';
        matches.slice(0, 6).forEach(product => {
            const imageUrl = `{{ url_for('static', filename='images/${product.image}') }}`;
            html += `
                <div class="live-search-item" data-product-id="${product.id}">
                    <div class="live-search-item-price">£${product.currentPrice.toFixed(2)}</div>
                    <div class="live-search-item-name">${this.escapeHtml(product.name)}</div>
                    <div class="live-search-item-discount">-${product.discountPercent}%</div>
                </div>
            `;
        });

        if (matches.length > 6) {
            html += `<div class="live-search-view-all">View all ${matches.length} results</div>`;
        } else if (matches.length > 0) {
            html += `<div class="live-search-view-all">View all results</div>`;
        }

        html += '</div>';
        dropdown.innerHTML = html;
        dropdown.style.display = 'block';

        // Add click handlers to items
        dropdown.querySelectorAll('.live-search-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const productId = item.dataset.productId;
                // Redirect to product detail page
                window.location.href = `/product/${productId}`;
            });
        });

        // Add click handler to "View all" link
        const viewAllBtn = dropdown.querySelector('.live-search-view-all');
        if (viewAllBtn) {
            viewAllBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                // Redirect to search results page with the search query
                const encodedQuery = encodeURIComponent(this.searchTerm);
                window.location.href = `/search-results?q=${encodedQuery}`;
            });
        }
    }

    /**
     * Hide live search dropdown
     */
    hideLiveSearchDropdown() {
        const dropdown = document.getElementById('live-search-dropdown');
        if (dropdown) {
            dropdown.style.display = 'none';
        }
    }

    /**
     * Escape HTML special characters
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Reset all filters
     */
    resetFilters() {
        this.activeFilters = {
            priceRanges: [],
            discounts: [],
            ratings: [],
            availability: []
        };
        this.searchTerm = '';
        this.currentSort = 'relevant';

        // Uncheck all checkboxes
        document.querySelectorAll('.header-filter-option input[type="checkbox"]').forEach(checkbox => {
            checkbox.checked = false;
        });

        // Remove active class from sort buttons
        document.querySelectorAll('.header-sort-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        // Clear search input
        const headerSearchInput = document.getElementById('headerSearch');
        if (headerSearchInput) {
            headerSearchInput.value = '';
        }

        this.applyFiltersAndSearch();
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.productSearchFilter = new ProductSearchFilter();
    console.log('Product search and filter initialized');
});
