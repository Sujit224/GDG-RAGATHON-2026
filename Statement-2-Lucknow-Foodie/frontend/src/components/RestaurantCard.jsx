import React from 'react';
import { Star, MapPin, Navigation, IndianRupee } from 'lucide-react';

export const RestaurantCard = ({ restaurant, onViewMap, className="" }) => {
    return (
        <div className={`bg-white rounded-xl border border-cardsTheme shadow-sm overflow-hidden flex flex-col transition-all hover:shadow-md hover:-translate-y-1 ${className}`}>
            <div className="p-4 flex-1 flex flex-col">
                <div className="flex justify-between items-start mb-2">
                    <h3 className="font-serif text-lg font-bold text-textTheme leading-tight">{restaurant.name}</h3>
                    <div className="flex bg-amber-100 text-amber-700 px-2 py-0.5 rounded text-xs font-bold items-center gap-1">
                        <Star size={12} className="fill-amber-500 text-amber-500"/>
                        {restaurant.rating}
                    </div>
                </div>
                
                <div className="flex items-center text-gray-500 text-xs mb-3 gap-1">
                    <MapPin size={12}/>
                    <span>{restaurant.area}</span>
                    <span className="mx-1">•</span>
                    <Navigation size={12} />
                    <span>{restaurant.distance_from_campus_km} km</span>
                </div>

                <div className="flex flex-wrap gap-2 mb-3">
                    <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full border ${restaurant.type === 'Veg' ? 'border-green-300 text-green-700 bg-green-50' : restaurant.type === 'Non-Veg' ? 'border-red-300 text-red-700 bg-red-50' : 'border-blue-300 text-blue-700 bg-blue-50'}`}>
                        {restaurant.type}
                    </span>
                    <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-gray-100 text-gray-700 flex items-center gap-0.5">
                        <IndianRupee size={10} /> {restaurant.budget_per_person_inr} for one
                    </span>
                </div>

                <div className="mt-auto pt-3 border-t border-gray-100">
                    <p className="text-xs text-gray-600 mb-3 line-clamp-2">
                        <span className="font-semibold text-gray-800">Must Try:</span> {restaurant.signature_dishes?.slice(0, 2).join(', ')}
                    </p>
                    <button 
                        onClick={() => onViewMap(restaurant)}
                        className="w-full py-2 bg-primary/10 hover:bg-primary/20 text-primary font-semibold text-sm rounded-lg transition-colors flex items-center justify-center gap-2"
                    >
                        <MapPin size={14} />
                        View on Map
                    </button>
                </div>
            </div>
        </div>
    );
};
