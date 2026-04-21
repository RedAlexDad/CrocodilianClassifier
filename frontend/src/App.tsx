import { Provider } from 'react-redux';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { store } from './app/store/store';
import { ClassifierWidget } from './widgets/Classifier/ClassifierWidget';
import './index.css';

const queryClient = new QueryClient();

function App() {
  return (
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <div className="app">
          <header className="header">
            <h1>Крокодилы 🐊</h1>
            <p>Классификатор: крокодил, аллигатор, кайман</p>
          </header>
          <main>
            <ClassifierWidget />
          </main>
        </div>
      </QueryClientProvider>
    </Provider>
  );
}

export default App;