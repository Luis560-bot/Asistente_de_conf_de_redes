import { Injectable } from '@nestjs/common';

@Injectable()
export class AppService {
  getHello(): string {
    return 'Hello World!';
  }

  async getIAResponse(message: string): Promise<string> {
    // Placeholder - será implementado por el equipo de IA
    return `Mensaje IA recibido: "${message}". Respuesta pending...`;
  }
}
