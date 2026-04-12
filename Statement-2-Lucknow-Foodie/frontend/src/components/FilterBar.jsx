import React from 'react';

export const FilterBar = ({ filters, setFilters }) => {
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFilters(prev => ({ ...prev, [name]: value }));
    };

    return (
        <div className="bg-white p-4 rounded-xl border border-cardsTheme shadow-sm mb-4">
            <h3 className="text-sm font-semibold mb-3 text-gray-700 uppercase tracking-wide">Filters</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <select name="diet" value={filters.diet || "All"} onChange={handleChange} className="w-full bg-gray-50 border border-gray-200 text-sm rounded-lg focus:ring-primary focus:border-primary block p-2">
                    <option value="All">All Diets</option>
                    <option value="Veg">Veg Only</option>
                    <option value="Non-Veg">Non-Veg</option>
                    <option value="Both">Both</option>
                </select>

                <select name="budget_max" value={filters.budget_max || ""} onChange={handleChange} className="w-full bg-gray-50 border border-gray-200 text-sm rounded-lg focus:ring-primary focus:border-primary block p-2">
                    <option value="">Any Budget</option>
                    <option value="100">Under ₹100</option>
                    <option value="300">Under ₹300</option>
                    <option value="500">Under ₹500</option>
                    <option value="1000">Under ₹1000</option>
                </select>

                <select name="area" value={filters.area || "All Areas"} onChange={handleChange} className="w-full bg-gray-50 border border-gray-200 text-sm rounded-lg focus:ring-primary focus:border-primary block p-2">
                    <option value="All Areas">All Areas</option>
                    <option value="Near Campus">Near Campus</option>
                    <option value="Gomti Nagar">Gomti Nagar</option>
                    <option value="Hazratganj">Hazratganj</option>
                    <option value="Aminabad">Aminabad</option>
                    <option value="Chowk">Chowk</option>
                    <option value="Vikas Nagar">Vikas Nagar</option>
                </select>

                <select name="sort_by" value={filters.sort_by || "rating"} onChange={handleChange} className="w-full bg-gray-50 border border-gray-200 text-sm rounded-lg focus:ring-primary focus:border-primary block p-2">
                    <option value="rating">Sort by Rating</option>
                    <option value="distance">Sort by Distance</option>
                    <option value="budget">Sort by Budget</option>
                </select>
            </div>
        </div>
    );
};
