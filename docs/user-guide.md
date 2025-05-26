# User Guide

## Getting Started

### Basic Usage

1. **Start the app**
   ```bash
   source venv/bin/activate && python voice_transcriber.py
   ```

2. **Position your cursor** where you want the text to appear

3. **Record and transcribe**:
   - Press and HOLD the Option/Alt key
   - Speak naturally
   - Release the key when done
   - Wait for transcription

4. **Exit the app**:
   - Press Ctrl+C to quit

### Tips for Best Results

1. **Speaking Tips**
   - Speak clearly and at a natural pace
   - Maintain consistent volume
   - Minimize background noise
   - Keep recordings under 30 seconds
   - Pause between sentences

2. **Recording Tips**
   - Hold Option key the entire time
   - Wait for "Recording..." message
   - Release when done speaking
   - Wait for "Transcribed" message before next recording

3. **Cursor Tips**
   - Click where you want text BEFORE recording
   - Ensure text field is active and editable
   - Test in simple text editor first

## Configuration

### Environment Variables

Edit your `.env` file to customize the app:

```env
# OpenAI API
OPENAI_API_KEY=your-api-key-here

# Audio Settings
SAMPLE_RATE=44100      # Audio quality (44100 or 16000)
CHUNK_SIZE=1024       # Buffer size (512-4096)

# Recording
MAX_RECORDING_TIME=300  # Maximum seconds
MAX_MEMORY_MB=100      # Memory limit

# Language
LANGUAGE=en           # Language code (en, es, fr, etc.)

# Text Processing
REMOVE_FILLER_WORDS=true
CUSTOM_FILLER_WORDS=basically,literally,actually

# Performance
TYPING_INTERVAL=0.01  # Delay between characters
```

### Language Support

Set `LANGUAGE` in `.env` to your preferred language:
- English: `en`
- Spanish: `es`
- French: `fr`
- German: `de`
- Auto-detect: `auto`

[Full list of language codes](https://platform.openai.com/docs/guides/speech-to-text/supported-languages)

### Filler Words

1. **Default filler words removed**:
   - um, uh, er, ah
   - like, you know
   - so, well
   - hmm, okay
   - actually, basically
   - literally, sort of
   - kind of, i mean

2. **Add custom filler words**:
   ```env
   CUSTOM_FILLER_WORDS=word1,word2,phrase1,phrase2
   ```

## Advanced Features

### Memory Management

- Set `MAX_MEMORY_MB` to control memory usage
- Default: 100MB
- Increase for longer recordings
- Decrease if memory issues occur

### Error Handling

The app includes:
- Automatic retries for API calls
- Device monitoring
- Resource cleanup
- Detailed logging

### Logging

- Check console output for status
- Error messages include suggestions
- Warning messages for potential issues
- Success messages confirm actions

## Troubleshooting

### Common Issues

1. **No transcription appears**:
   - Check cursor position
   - Verify text field is editable
   - Check permissions
   - Try a different application

2. **Audio issues**:
   - Check microphone permissions
   - Test microphone in System Settings
   - Try different audio settings
   - Check hardware connections

3. **API errors**:
   - Verify API key in `.env`
   - Check internet connection
   - Monitor API usage limits
   - Check OpenAI service status

### Performance Optimization

1. **For faster processing**:
   - Keep recordings short
   - Use recommended audio settings
   - Close unnecessary applications
   - Monitor system resources

2. **For better accuracy**:
   - Speak clearly
   - Use proper microphone
   - Minimize background noise
   - Choose appropriate language

## Cost Management

### API Usage

- $0.006 per minute of audio
- Example costs:
  - 1 minute = $0.006
  - 1 hour = $0.36
  - 100 minutes/day = $18/month

### Monitoring

1. Track usage:
   - Visit [OpenAI Dashboard](https://platform.openai.com/usage)
   - Monitor daily/monthly usage
   - Set up usage alerts

2. Optimize costs:
   - Keep recordings concise
   - Use push-to-talk effectively
   - Monitor and adjust usage patterns

## Privacy Considerations

1. **Data Handling**:
   - Audio sent to OpenAI
   - No local storage
   - Temporary files deleted
   - No conversation history

2. **Best Practices**:
   - Avoid sensitive information
   - Use in private environment
   - Monitor surroundings
   - Review transcribed text

## Support

For issues:
1. Check this guide
2. Review error messages
3. Check [GitHub Issues](https://github.com/tommyyau/wispr-flow-lite/issues)
4. Submit new issue if needed 