import { configureStore } from '@reduxjs/toolkit';
import classifierReducer from '@/features/classifier/classifierSlice';
import segmenterReducer from '@/features/segmentation/segmentationSlice';

export const store = configureStore({
  reducer: {
    classifier: classifierReducer,
    segmenter: segmenterReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;