///////////////////  SURFACES FRAGMENT SHADER /////////////////////////

uniform samplerBuffer Misc;
uniform samplerBuffer Proj_Params;
uniform samplerBuffer realtimeData;
uniform samplerBuffer PixframeControl;

uniform int ProjectorBufferSize;
uniform ivec3 ViewportChanIndicies;
uniform int NumPasses;
uniform float selectionPulse;
uniform int maskPreviewIndex;
ivec2 	PixelCoords2D;
uniform int NumMasks;
uniform int NumPixFrameContribs;

uniform sampler2D item0;
uniform sampler2D item1;
uniform sampler2D item2;
uniform sampler2D item3;
uniform sampler2D item4;
uniform sampler2D item5;
uniform sampler2D item6;
uniform sampler2D item7;
uniform sampler2D item8;
uniform sampler2D item9;
uniform sampler2D item10;
uniform sampler2D item11;
uniform sampler2D item12;
uniform sampler2D item13;
uniform sampler2D item14;
uniform sampler2D item15;

uniform sampler2DArray MASKS;
uniform sampler2DArray PIXFRAMES;

#define ProjTex0 item0
#define ProjTex1 item1
#define ProjTex2 item2
#define ProjTex3 item3
#define ProjTex4 item4
#define ProjTex5 item5
#define ProjTex6 item6
#define ProjTex7 item7
#define ProjTex8 item8
#define ProjTex9 item9
#define ProjTex10 item10
#define ProjTex11 item11
#define ProjTex12 item12
#define ProjTex13 item13
#define ProjTex14 item14
#define ProjTex15 item15

#include <GLSL_SamplerFunctions>


in Vertex
{
	// vec4 xyzw;
	vec3 rgbIndicies;
	vec4 coords[16];
	flat int surfIndex;
	flat bool Selected;
	// float DEBUG;
} iVert;

out vec4 fragColor;
void main()
{
	TDCheckDiscard();

	// we get the world space coordinates of the Pix. We might eventually want to get other coordinate sets
	float 	CoordsIndex 	= 0; // this was used to generate projector chase but this is not applicable on surfaces.

	bool Selected = iVert.Selected;

	// get some fixture parameters.
	int 	UtilizationMask = 1; // this used to tell us if a pixel was empty or not. with geometry, we do not need this anymore.
	int 	currentChanIndex= 0; // we do not need this anymore as we are not writing out to a 1 channel buffer, but a standard rgb buffer.

	ivec3 RGB_IDs = ivec3(iVert.rgbIndicies);

	vec4 finalColor 		= vec4(0,0,0,1);
	vec4 	color 			= vec4(0.0);

	// get number of pixframes by dividing the length of the control buffer by the number of attributes each frame is represented by.
	int NumberOfControls 	= 3; // 3 controls per contribution. [pixframeIndex, pixframeIntensity, pixframeBlendMode]

	ProjectorObject pObj;

	// vec4 debugColor = vec4(0,0,0,1);
	
	for( int i=0; i<NumPasses; i++ )
	{

	 	// this will be set in the eventual for loop.
	 	vec4	realtimeDataFetch 	= texelFetch(realtimeData, i);
		float 	FadeScale 			= realtimeDataFetch.x;
		int 	TextureIndex 		= int(realtimeDataFetch.y);
		int 	projectorIndex 		= int(realtimeDataFetch.z);
		bool 	constantColor 		= bool(realtimeDataFetch.w);

		if( FadeScale > 0 ){

			// get the projector object by index.
			pObj = GetProjector(projectorIndex);

			if( pObj.Projectoractive == true ){

				// convert the world space Pix coordinates into projector space 0:1
				vec4 ProjectorSpaceCoordinates = iVert.coords[i];

				// handles the wrapping, or mirroring of uvs in glsl, so we can control this per projector.
				ProjectorSpaceCoordinates = Apply_Extend_Modes( ProjectorSpaceCoordinates , pObj );

				// this function returns a mask, 0 or 1, that represents where the projector is hitting, where it isnt(behind), etc.
				float ProjectorCullMask = Cull_Pix_Against_Projector( ProjectorSpaceCoordinates , pObj , UtilizationMask );

				// generates the projector mask. Will be 1 if the fixture has no masks, otherwise will try to bool equate as a mask.
				vec3 projectorMaskV2 = vec3(1);
				projectorMaskV2.r = Generate_Projector_Masks_V2( pObj , RGB_IDs.r , iVert.surfIndex );
				projectorMaskV2.g = Generate_Projector_Masks_V2( pObj , RGB_IDs.g , iVert.surfIndex );
				projectorMaskV2.b = Generate_Projector_Masks_V2( pObj , RGB_IDs.b , iVert.surfIndex );

				// debugColor.r = projectorMaskV2;

				vec4 ProjectorSampledTexture = vec4(0);
				vec4 constColor = vec4(0);
				if( constantColor == true ){

				 	// this function contributes the constant color, previously known as color override to the appropriate channels.
					constColor = Contribute_ConstantColor_To_Buffer( pObj , RGB_IDs , ProjectorCullMask );

				}

				else{
				 	// sample the correct projector texture based on index, and then apply the mask.
					// ProjectorSampledTexture = Sample_Projector_Texture( ProjectorSpaceCoordinates , ProjectorCullMask , TextureIndex , FadeScale );
					ProjectorSampledTexture = Sample_Projector_Texture( ProjectorSpaceCoordinates , ProjectorCullMask , TextureIndex );

				}

				// this function contributes the sampled texture, to the buffer, while masking it to only the pixels who contain that channel index.
				// color = Contribute_Texture_To_Buffer( color , ProjectorSampledTexture , pObj , RGB_IDs , constColor , projectorMaskV2 );
				vec4 newVal = Contribute_Texture_To_Buffer( color , ProjectorSampledTexture , pObj , RGB_IDs , constColor , projectorMaskV2 );
				color = mix( color , newVal , FadeScale );

			}

			// break;

		}

	}

	// applies the pixframes to their respective routing channels.
	color.rgb = Apply_PixFrames( color , iVert.surfIndex , NumPixFrameContribs , NumberOfControls );


	finalColor += color;


	// this function causes us to temporarily switch into a preview mode for visualizing our masks. when a user hovers a mask in the mask editor, it highlights in viewport.
	finalColor = Contribute_MaskHighlight_To_Buffer( finalColor, iVert.surfIndex , RGB_IDs );

	// this function modifies the color buffer, to overwrite pure green where the fixture is selected, or the fixture's Pix is selected while in Pix mode.
	finalColor = Contribute_SelectionHighlight_To_Buffer( finalColor, Selected );
	// finalColor.rgb = vec3( iVert.Selected , 0 , 0 );

	// DEBUG
	// finalColor = vec4(1,0,0,1);
	// finalColor = debugColor;


	fragColor = TDOutputSwizzle(finalColor);
	
}

