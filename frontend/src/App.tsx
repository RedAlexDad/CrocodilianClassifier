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
        <div className="fixed-header">
          <div className="container">
            <div className="header-title">Классификатор: крокодил, аллигатор, кайман</div>
          </div>
        </div>

        <div className="container">
          <ClassifierWidget />
        </div>

        <div className="fixed-footer">
          <div className="container">
            Домашнее задание №1 - Классификация изображений
          </div>
        </div>
      </QueryClientProvider>
    </Provider>
  );
}

export default App;