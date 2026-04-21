import { configureStore } from '@reduxjs/toolkit';
import classifierReducer from '@/features/classifier/classifierSlice';

export const store = configureStore({
  reducer: {
    classifier: classifierReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;