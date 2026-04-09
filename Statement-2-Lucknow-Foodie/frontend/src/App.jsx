import React, { useState, useEffect } from 'react';
import { ChefHat, Map as MapIcon, Compass } from 'lucide-react';
import { FilterBar } from './components/FilterBar';
import { RestaurantCard } from './components/RestaurantCard';
import { ChatWindow } from './components/ChatWindow';
import { MapView } from './components/MapView';
import { getRestaurants } from './api/client';
import { useChat } from './hooks/useChat';

function App() {
  const [filters, setFilters] = useState({ diet: 'All', budget_max: '', area: 'All Areas', sort_by: 'rating' });
  const [restaurants, setRestaurants] = useState([]);
  const [showMap, setShowMap] = useState(false);
  const [focusRestaurant, setFocusRestaurant] = useState(null);
  const { messages, sendMessage, loading, clearChat } = useChat();

  useEffect(() => {
    const fetchFiltered = async () => {
      try {
        const data = await getRestaurants(filters);
        setRestaurants(data);
      } catch (err) {
        console.error("Failed to fetch restaurants", err);
      }
    };
    fetchFiltered();
  }, [filters]);

  const handleViewMap = (r) => {
    setShowMap(true);
    setFocusRestaurant(r);
  };

  return (
    <div className="min-h-screen flex flex-col pt-4 px-4 bg-[#f4ece3]/40 pb-4">
      {/* Header */}
      <header className="max-w-7xl w-full mx-auto mb-4 flex items-center gap-3 bg-white p-4 rounded-xl border border-cardsTheme shadow-sm">
        <div className="w-10 h-10 bg-primary text-white rounded-lg flex items-center justify-center flex-shrink-0">
          <ChefHat size={24} />
        </div>
        <div>
          <h1 className="font-serif text-2xl font-bold text-textTheme leading-none">Lucknow Foodie Guide</h1>
          <p className="text-gray-500 text-sm mt-1">Your AI food buddy near IIIT Lucknow</p>
        </div>
      </header>

      {/* Main Layout Area */}
      <main className="max-w-7xl w-full mx-auto flex-1 flex flex-col lg:flex-row gap-4 h-[calc(100vh-120px)]">
        
        {/* Left Panel: Explorer (40%) */}
        <div className="w-full lg:w-[45%] flex flex-col h-full overflow-hidden">
          <FilterBar filters={filters} setFilters={setFilters} />
          
          <div className="flex justify-between items-center mb-3">
            <h2 className="font-bold text-gray-800 flex items-center gap-2 text-sm">
              <Compass size={16} className="text-primary"/> 
              Explore Places ({restaurants.length})
            </h2>
            <button 
              onClick={() => setShowMap(!showMap)}
              className="px-3 py-1.5 text-xs font-semibold rounded-lg border border-gray-200 bg-white shadow-sm hover:bg-gray-50 flex items-center gap-2"
            >
              <MapIcon size={14} />
              {showMap ? "Hide Map" : "Show Map"}
            </button>
          </div>

          <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar flex flex-col gap-3 pb-8">
            {showMap && (
              <div className="mb-4 shrink-0">
                <MapView 
                  restaurants={restaurants} 
                  focusRestaurant={focusRestaurant}
                  onMapClose={() => setShowMap(false)} 
                />
              </div>
            )}
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pb-4">
              {restaurants.map(r => (
                <RestaurantCard 
                  key={r.id} 
                  restaurant={r} 
                  onViewMap={handleViewMap} 
                />
              ))}
              {restaurants.length === 0 && (
                <div className="col-span-full py-10 text-center text-gray-500 bg-white rounded-xl border border-dashed border-gray-300">
                  No places match your filters. Try adjusting them!
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Panel: Chat (60%) */}
        <div className="w-full lg:w-[55%] h-full min-h-[500px]">
          <ChatWindow 
            messages={messages}
            loading={loading}
            onSendMessage={sendMessage}
            onClear={clearChat}
            onViewMap={handleViewMap}
          />
        </div>

      </main>
      
      <style dangerouslySetInnerHTML={{__html: `
        .custom-scrollbar::-webkit-scrollbar { width: 6px; height: 6px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 10px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #9ca3af; }
      `}} />
    </div>
  );
}

export default App;
